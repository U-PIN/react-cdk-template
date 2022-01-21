from constructs import Construct
from aws_cdk import (
  Stage
)
from frontend_stack import FrontendStack

class FrontendPipelineStage(Stage):

  @property
  def s3_bucket_name(self):
    return self._s3_bucket_name

  @property
  def app_url(self):
    return self._app_url

  def __init__(self, scope: Construct, id: str, **kwargs):
    super().__init__(scope, id, **kwargs)

    frontend = FrontendStack(self, "Frontend")
    self._app_url = frontend.app_url
    self._s3_bucket_name = frontend.s3_bucket_name