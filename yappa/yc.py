import os

import yandexcloud
from google.protobuf.duration_pb2 import Duration
from google.protobuf.empty_pb2 import Empty
from yandex.cloud.access.access_pb2 import AccessBinding, \
    ListAccessBindingsRequest, \
    SetAccessBindingsMetadata, SetAccessBindingsRequest, Subject
from yandex.cloud.serverless.functions.v1.function_pb2 import (Function,
                                                               Package,
                                                               Resources,
                                                               Version)
from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
    CreateFunctionMetadata, CreateFunctionRequest,
    CreateFunctionVersionMetadata, CreateFunctionVersionRequest,
    DeleteFunctionMetadata, DeleteFunctionRequest, ListFunctionsRequest)
from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import \
    FunctionServiceStub

from yappa.utils import convert_size_to_bytes



def load_credentials(**credentials):
    environ_credentials = {
        "token": os.environ.get("YC_TOKEN"),
        "cloud_id": os.environ.get("YC_CLOUD"),
        "folder_id": os.environ.get("YC_FOLDER"),
    }
    environ_credentials.update(**credentials)
    return environ_credentials


class YC:
    def __init__(self, token, folder_id, cloud_id):
        self.sdk = yandexcloud.SDK(token=token)
        self.function_service = self.sdk.client(FunctionServiceStub)
        self.folder_id = folder_id
        self.cloud_id = cloud_id
        # TODO do i need cloud id?

    def get_functions(self, filter_=None):
        functions = self.function_service.List(
            ListFunctionsRequest(folder_id=self.folder_id,
                                 filter=filter_)).functions
        return {f.name: dict(id=f.id, url=f.http_invoke_url) for f in functions}

    def create_function(self, name, description="", is_public=True):
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
        self.set_access(function.id, is_public)
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

    def set_access(self, function_id, is_public=True):
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

    def is_function_public(self, function_id):
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
                                entrypoint, bucket_name, object_name,
                                memory="128MB", service_account_id=None,
                                timeout=None, named_service_accounts=None,
                                environment=None, **kwargs):
        operation = self.function_service.CreateVersion(
            CreateFunctionVersionRequest(
                function_id=function_id,
                runtime=runtime,
                description=description,
                entrypoint=entrypoint,
                resources=Resources(memory=convert_size_to_bytes(memory)),
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
