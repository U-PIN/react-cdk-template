from constructs import Construct
from aws_cdk import (
  Stage
)
from backend_stack import BackendStack

class BackendPipelineStage(Stage):

  @property
  def hello_api_endpoint(self):
    return self._hello_api_endpoint

  def __init__(self, scope: Construct, id: str, **kwargs):
    super().__init__(scope, id, **kwargs)

    backend = BackendStack(self, "Backend")
    self._hello_api_endpoint = backend.hello_api_endpoint
