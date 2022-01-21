from constructs import Construct
from aws_cdk import (
  Stack,
  CfnOutput,
  aws_lambda as _lambda,
  aws_apigateway as apigw,
)

class BackendStack(Stack):

  @property
  def hello_api_endpoint(self):
    return self._hello_api_endpoint

  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    hello_lambda = _lambda.Function(
      self, 'HelloHandler',
      runtime=_lambda.Runtime.PYTHON_3_9,
      code=_lambda.Code.from_asset('lib/lambda'),
      handler='hello.handler',
    )

    hello_api = apigw.LambdaRestApi(
      self, 'Endpoint',
      handler=hello_lambda
    )

    self._hello_api_endpoint = CfnOutput(
      self, 'HelloAPIEndpoint',
      value=hello_api.url
    )
