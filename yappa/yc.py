import os

import yandexcloud
from yandex.cloud.serverless.functions.v1.function_pb2 import Function
from yandex.cloud.serverless.functions.v1.function_service_pb2 import \
    CreateFunctionMetadata, CreateFunctionRequest, DeleteFunctionMetadata, \
    DeleteFunctionRequest, \
    ListFunctionsRequest
from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import \
    FunctionServiceStub


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
