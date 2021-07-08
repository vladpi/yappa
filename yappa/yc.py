import json
import os
from contextlib import suppress
from typing import Iterable

import yandexcloud
from click import ClickException
from google.protobuf.duration_pb2 import Duration
from google.protobuf.empty_pb2 import Empty
from yandex.cloud.access.access_pb2 import (
    AccessBinding,
    ListAccessBindingsRequest,
    SetAccessBindingsMetadata, SetAccessBindingsRequest, Subject,
)
from yandex.cloud.iam.v1.awscompatibility.access_key_service_pb2 import \
    CreateAccessKeyRequest
from yandex.cloud.iam.v1.awscompatibility.access_key_service_pb2_grpc import \
    AccessKeyServiceStub
from yandex.cloud.serverless.apigateway.v1.apigateway_pb2 import ApiGateway
from yandex.cloud.serverless.functions.v1.function_pb2 import (
    Function,
    Package,
    Resources,
    Version,
)
from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
    CreateFunctionMetadata, CreateFunctionRequest,
    CreateFunctionVersionMetadata, CreateFunctionVersionRequest,
    DeleteFunctionMetadata, DeleteFunctionRequest,
    GetFunctionVersionByTagRequest, ListFunctionsRequest,
)
from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import \
    FunctionServiceStub

from yappa.config_generation import get_yc_entrypoint
from yappa.handle_wsgi import DEFAULT_CONFIG_FILENAME, load_yaml
from yappa.settings import DEFAULT_ACCESS_KEY_FILE, DEFAULT_SERVICE_ACCOUNT
from yappa.utils import convert_size_to_bytes


class YC:
    def __init__(self, folder_id, token=None,
                 service_account_key=None):
        self.sdk = yandexcloud.SDK(token=token,
                                   service_account_key=service_account_key)
        self.service_account_id = (service_account_key.get("service_account_id")
                                   if service_account_key else None)
        self.function_service = self.sdk.client(FunctionServiceStub)
        self.key_service = self.sdk.client(AccessKeyServiceStub)
        self.folder_id = folder_id
        self.function = None
        self.gateway = None

    @classmethod
    def setup(cls, token=None, config={}):
        """
        - token can be passed directly or read from YC_OAUTH env variable
        - if couldn't get token, trying to read access key from .yc file
        - folder_id is read from yappa_config.yaml or read from
          YC_FOLDER env variable
        """
        credentials = {
            "token": token or os.environ.get("YC_OAUTH"),
            "folder_id": os.environ.get("YC_FOLDER"),
        }
        if not credentials["token"]:
            with suppress(FileNotFoundError):
                with open(DEFAULT_ACCESS_KEY_FILE, "r+") as f:
                    credentials["service_account_key"] = json.loads(f.read())
        if not (credentials["token"] or credentials["service_account_key"]):
            raise ClickException("Sorry. Looks like you didn't provide OAuth "
                                 "token or path to access key")

        folder_id = config.get("folder_id") or os.environ.get("YC_FOLDER")
        if not folder_id:
            raise ClickException("Sorry. Couldn't load folder_id from config "
                                 "file or YC_FOLDER environment variable")
        return cls(folder_id=folder_id, **credentials)

    def get_function(self, name=None) -> Function:
        """
        convenience method to get deployed function
        """
        if not self.function:
            for f in self.get_functions():
                if f.name == name:
                    self.function = f
                    return f
        raise ValueError(f"Oops. Didn't find any function by name {name}")

    def get_functions(self, filter_=None) -> Iterable[Function]:
        functions = self.function_service.List(
            ListFunctionsRequest(folder_id=self.folder_id,
                                 filter=filter_)).functions
        return functions

    def create_function(self, name, description="",
                        is_public=True) -> Function:
        operation = self.function_service.Create(CreateFunctionRequest(
            folder_id=self.folder_id,
            name=name,
            description=description,
        ))
        operation_result = self.sdk.wait_operation_and_get_result(
            operation,
            response_type=Function,
            meta_type=CreateFunctionMetadata,
        )
        function = operation_result.response
        self.set_function_access(function.id, is_public)
        self.function = function
        return function

    def delete_function(self, function_id):
        operation = self.function_service.Delete(DeleteFunctionRequest(
            function_id=function_id
        ))
        operation_result = self.sdk.wait_operation_and_get_result(
            operation,
            response_type=Function,
            meta_type=DeleteFunctionMetadata,
        )
        return operation_result.response

    def set_function_access(self, function_id, is_public=True):
        if is_public:
            access_bindings = [AccessBinding(
                role_id='serverless.functions.invoker',
                subject=Subject(
                    id="allUsers",
                    type="system",
                )
            )]
        else:
            access_bindings = []
        operation = self.function_service.SetAccessBindings(
            SetAccessBindingsRequest(
                resource_id=function_id,
                access_bindings=access_bindings
            ))
        self.sdk.wait_operation_and_get_result(
            operation,
            response_type=Empty,
            meta_type=SetAccessBindingsMetadata,
        )
        return is_public

    def is_function_public(self, function_id) -> bool:
        access_bindings = self.function_service.ListAccessBindings(
            ListAccessBindingsRequest(
                resource_id=function_id
            )).access_bindings
        for binding in access_bindings:
            if binding.role_id == 'serverless.functions.invoker':
                subject = binding.subject
                return subject.id == "allUsers"
        return False

    def create_function_version(self, function_id, runtime, description,
                                bucket_name, object_name,
                                application_type="wsgi",
                                memory="128MB", service_account_id=None,
                                timeout=None, named_service_accounts=None,
                                environment=None) -> Version:
        operation = self.function_service.CreateVersion(
            CreateFunctionVersionRequest(
                function_id=function_id,
                runtime=runtime,
                description=description,
                entrypoint=get_yc_entrypoint(application_type),
                resources=Resources(
                    memory=convert_size_to_bytes(memory)),
                execution_timeout=Duration(seconds=timeout),
                service_account_id=service_account_id,
                package=Package(bucket_name=bucket_name,
                                object_name=object_name),
                named_service_accounts=named_service_accounts,
                environment=environment
            ))
        operation_result = self.sdk.wait_operation_and_get_result(
            operation,
            response_type=Version,
            meta_type=CreateFunctionVersionMetadata,
        )
        return operation_result.response

    def get_latest_version(self, function_id) -> Version:
        version = self.function_service.GetVersionByTag(
            GetFunctionVersionByTagRequest(
                function_id=function_id,
                tag="$latest",
            ))
        return version

    def get_gateway(self, name=None) -> ApiGateway:
        """
         convenience method to get deployed gateway
         """
        if not self.gateway:
            for gw in self.get_gateways():
                if gw.name == name:
                    self.gateway = gw
                    return gw
        raise ValueError(f"Oops. Didn't find any gateway by name {name}")

    def get_gateways(self) -> Iterable[ApiGateway]:
        pass

    def create_gateway(self, name, openapi_spec, description="") -> ApiGateway:
        gateway = None  # TODO implement
        self.gateway = gateway

    def update_gateway(self, gateway_id, description,
                       openapi_spec) -> ApiGateway:
        pass

    def delete_gateway(self, gateway_id):
        pass

    def ensure_service_account(self,
                               service_account_name=DEFAULT_SERVICE_ACCOUNT):
        """
        if there is not account with such name, creates such account
        """

    def get_s3_key(self, service_account_name=DEFAULT_SERVICE_ACCOUNT,
                   description="yappa upload"):
        """
        if YC was instantiated with OAuth token: service account id is used
        else: it means we are already using service account, hence generate
        access key for using service account
        """
        if not self.service_account_id:
            self.service_account_id = self.ensure_service_account(
                service_account_name).id
        response = self.key_service.Create(
            CreateAccessKeyRequest(service_account_id=self.service_account_id,
                                   description=description))
        return {
            "aws_access_key_id": response.access_key.key_id,
            "aws_secret_access_key": response.secret
        }
