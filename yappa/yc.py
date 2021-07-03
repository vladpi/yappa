import os

import yandexcloud
from google.protobuf.duration_pb2 import Duration
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


def convert_size_to_bytes(size):
    # TODO add tests
    raise NotImplementedError()
    multipliers = {
        'kb': 1024,
        'mb': 1024 * 1024,
        'gb': 1024 * 1024 * 1024,
        'tb': 1024 * 1024 * 1024 * 1024
    }

    for suffix in multipliers:
        if size.lower().endswith(suffix):
            return int(size[0:-len(suffix)]) * multipliers[suffix]
    else:
        if size.lower().endswith('b'):
            return int(size[0:-1])

    try:
        return int(size)
    except ValueError:  # for example "1024x"
        print('Malformed input!')
        exit()


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

    def create_function(self, name, description=""):
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
        return operation_result.response

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
