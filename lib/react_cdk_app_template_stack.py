from aws_cdk import (
    Stack,
    SecretValue,
    pipelines as pipelines,
)
from constructs import Construct

class ReactCdkAppTemplateStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)




