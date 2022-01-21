from aws_cdk import (
  Stack,
  SecretValue,
  pipelines as pipelines,
  aws_iam as iam,
)
from constructs import Construct
from backend_pipeline_stage import BackendPipelineStage
from frontend_pipeline_stage import FrontendPipelineStage

class PipelineStack(Stack):

  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    repository = "U-PIN/react-cdk-template"
    branch = "main"

    pipeline = pipelines.CodePipeline(
      self,
      "Pipeline",
      synth=pipelines.ShellStep(
        "Synth",
        input=pipelines.CodePipelineSource.git_hub(
          repository,
          branch,
          authentication=SecretValue.secrets_manager("GitHubOAuthToken")
        ),
        commands = [
          "npm install -g aws-cdk",
          "pip install -r requirements.txt",
          "npx cdk synth"
        ]
      )
    )

    backend = BackendPipelineStage(self, "DeployBackend")
    backend_stage = pipeline.add_stage(backend)

    frontend = FrontendPipelineStage(self, "DeployFrontend")
    frontend_stage = pipeline.add_stage(frontend)
    frontend_stage.add_post(
      pipelines.CodeBuildStep(
        "BuildAndDeployWebAppToS3",
        env_from_cfn_outputs={
          "S3_BUCKET": frontend.s3_bucket_name,
          "HELLO_API": backend.hello_api_endpoint
        },
        commands=[
          "cd frontend",
          'echo REACT_APP_HELLO_API="$HELLO_API" >> .env',
          "npm install",
          "npm run build",
          "aws s3 sync build s3://$S3_BUCKET/"
        ],
        role_policy_statements=[
          iam.PolicyStatement(
            actions=["s3:*"],
            resources=["*"]
          )
        ]
      )
    )


