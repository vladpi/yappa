import logging
from typing import Iterable

from yandex.cloud.serverless.apigateway.v1.apigateway_pb2 import ApiGateway

logger = logging.getLogger(__name__)


class YcGatewayMixin:
    sdk = None
    folder_id = None

    def get_gateway(self, name=None) -> ApiGateway:
        """
         convenience method to get deployed gateway
         """
        if not self.gateway:
            for gw in self._get_gateways():
                if gw.name == name:
                    self.gateway = gw
        if self.getaway:
            return self.gateway
        raise ValueError(f"Oops. Didn't find any gateway by name {name}")

    def _get_gateways(self) -> Iterable[ApiGateway]:
        pass

    def create_gateway(self, gateway_name, openapi_spec,
                       description="") -> ApiGateway:
        gateway = None  # TODO implement
        self.gateway = gateway

    def update_gateway(self, gateway_name, description,
                       openapi_spec) -> ApiGateway:
        pass
