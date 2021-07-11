import logging
from contextlib import suppress
from typing import Iterable

from google.protobuf.duration_pb2 import Duration
from google.protobuf.empty_pb2 import Empty
from yandex.cloud.access.access_pb2 import (
    AccessBinding,
    ListAccessBindingsRequest,
    SetAccessBindingsMetadata, SetAccessBindingsRequest, Subject,
)
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

from yappa.utils import convert_size_to_bytes

logger = logging.getLogger(__name__)


class YcFunctionsMixin:
    sdk = None
    folder_id = None

    def get_function(self, name) -> Function:
        """
        convenience method to get deployed function
        """

        for f in self._get_functions():
            if f.name == name:
                return f
        raise ValueError(f"Oops. Didn't find any function by name {name}")

    def _get_functions(self, filter_=None) -> Iterable[Function]:
        functions = self.sdk.client(FunctionServiceStub).List(
            ListFunctionsRequest(folder_id=self.folder_id,
                                 filter=filter_)).functions
        return functions

    def create_function(self, name, description="", is_public=True) -> Function:
        with suppress(ValueError):
            function = self.get_function(name)
            return function, False
        operation = self.sdk.client(FunctionServiceStub).Create(
            CreateFunctionRequest(
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
        self._set_function_access(function.id, is_public)
        return function, True

    def delete_function(self, function_id):
        operation = self.sdk.client(FunctionServiceStub).Delete(
            DeleteFunctionRequest(
                function_id=function_id
            ))
        operation_result = self.sdk.wait_operation_and_get_result(
            operation,
            response_type=Function,
            meta_type=DeleteFunctionMetadata,
        )
        return operation_result.response

    def _set_function_access(self, function_id, is_public=True):
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
        operation = self.sdk.client(FunctionServiceStub).SetAccessBindings(
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

    def _is_function_public(self, function_id) -> bool:
        access_bindings = self.sdk.client(
            FunctionServiceStub).ListAccessBindings(
            ListAccessBindingsRequest(
                resource_id=function_id
            )).access_bindings
        for binding in access_bindings:
            if binding.role_id == 'serverless.functions.invoker':
                subject = binding.subject
                return subject.id == "allUsers"
        return False

    def create_function_version(self, function_name, runtime, description,
                                bucket_name, object_name,
                                entrypoint,
                                memory="128MB", service_account_id=None,
                                timeout=None, named_service_accounts=None,
                                environment=None) -> Version:
        function = self.get_function(function_name)
        operation = self.sdk.client(FunctionServiceStub).CreateVersion(
            CreateFunctionVersionRequest(
                function_id=function.id,
                runtime=runtime,
                description=description,
                entrypoint=entrypoint,
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
        version = self.sdk.client(FunctionServiceStub).GetVersionByTag(
            GetFunctionVersionByTagRequest(
                function_id=function_id,
                tag="$latest",
            ))
        return version
