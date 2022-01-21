# Template for React + CDK Application

This is a template for React web application that has backend and frontend hosting resources defined by CDK, which also enables you to CI/CD your application with CDK Pipeline. You can simplify develop your backend APIs (i.e. ones that consist of API Gatway, Lambda, and DynamoDB) with CDK and pass the API endpoints to React app hosted on CloudFront and S3 that are also deployed by CDK. 


## File Structure

* `frontend/`: React app project root directory created by `create-react-app`
* `bin/`: CDK bin directory
  * `app.py`: The entrypoint of CDK application
* `lib/`: CDK stack and lambda definition directory
  * `backend_stack.py`: Defines backend resources. You can add any backend resource here. This template already has sample hello api
  * `backend_pipeline_stage.py`: Defines deploy pipeline stage for backend resources
  * `frontend_stack.py`: Defines frontend hosting resources; CloudFront, S3, and Route53
  * `frontend_pipeline_stage.py`: Defines deploy pipeline stage for frontend resources
  * `pipeline_stack.py`: Defines CodePipeline pipeline to build and deploy CDK defined resources and React Web application all at once
* `configure.py`: Configuration script for your app
* `config.params.json`: Config file used by `configure.py`
* `requirements.txt`: Dependency config file for Python packages. By default, `aws-cdk-lib`, `constructs`, and `boto3` are included


## Deployment Steps

### 1. Python virtualenv setup

Run following commands in the project root directory to install venv and activate it: 

```
$ python3 -m venv .venv
$ source .venv/bin/activate
```

### 2. Install dependencies

To install Python dependencies, simply run `pip install -r requirements.txt`. 

```
$ pip install -r requirements.txt
```

If you want to build and test your React web application locally, you need to install npm packages as well. 

```
$ cd frontend
$ cd npm install
```

### 3. Run configuration script

This template allows you to define some parameters for your application. Parameters are defined in `config.params.json` and you can add one as you like. The parameters are stored in SSM Parameter Store by `configure.py` and referred by CDK stack.  
SSM parameter name syntax is something like `/YourAppName/ParameterName` and `/YourAppName/` part is referred from `Namespace` field in `config.params.json`. You can simply replace `ReactCDKAppTemplate` with your own application name so that parameters in SSM Parameter Store won't conflict across applications.  
  
By default, `config.params.json` looks like this: 

```
{
  "Namespace": "/ReactCDKAppTemplate/",
  "Parameters": [
    {
      "Name": "CloudFrontAliasCertArn",
      "CLIFormat": "cloudfront-alias-cert-arn",
      "Description": "The ARN for the ACM certificate used for CloudFront destribution"
    },
    {
      "Name": "CloudFrontDomainName",
      "CLIFormat": "cloudfront-domain-name",
      "Description": "The domain name for CloudFront destribution"
    },
    {
      "Name": "HostedZoneName",
      "CLIFormat": "hosted-zone-name",
      "Description": "The name of Route 53 Hosted Zone"
    },
    {
      "Name": "HostedZoneId",
      "CLIFormat": "hosted-zone-id",
      "Description": "The ID of Route 53 Hosted Zone"
    }
  ],
  "DefaultOptions": [
    {
      "CLIFormat": "delete",
      "ShortCLIFormat": "d",
      "Action": "store_true",
      "Help": "delete all AWS SSM Parameters (after CDK stack was destroyed)"
    },
    {
      "CLIFormat": "interactive",
      "ShortCLIFormat": "i",
      "Action": "store_true",
      "Help": "run in interactive mode"
    },
    {
      "CLIFormat": "test",
      "ShortCLIFormat": "t",
      "Action": "store_true",
      "Help": "run in test mode (only creates config.cache.json, but does not store parameters to SSM Parameter Store)"
    }
  ]
}
```

To store parameters in SSM Parameter Store, run `python configure.py -i` that enables you to store parameters in interactive mode: 

```
$ python configure.py -i
```

You can view details of this script with `-h` option as well. 

```
$ python configure.py -h
usage: Usage: python configure.py [--help] [--delete] [--interactive] [--test] [--cloudfront-alias-cert-arn <value>] [--cloudfront-domain-name <value>] [--hosted-zone-name <value>] [--hosted-zone-id <value>]

Use this script for configuring SSM parameters for CDK deployment.

optional arguments:
  -h, --help            show this help message and exit
  -d, --delete          delete all AWS SSM Parameters (after CDK stack was destroyed)
  -i, --interactive     run in interactive mode
  -t, --test            run in test mode (only creates config.cache.json, but does not store parameters to SSM Parameter
                        Store)
  --cloudfront-alias-cert-arn CLOUDFRONT_ALIAS_CERT_ARN
                        The ARN for the ACM certificate used for CloudFront destribution
  --cloudfront-domain-name CLOUDFRONT_DOMAIN_NAME
                        The domain name for CloudFront destribution
  --hosted-zone-name HOSTED_ZONE_NAME
                        The name of Route 53 Hosted Zone
  --hosted-zone-id HOSTED_ZONE_ID
                        The ID of Route 53 Hosted Zone
```


### 4. Specify your GitHub repository information

In `lib/pipeline_stack.py`, you need to specify your repository related information.  
By default, `lib/pipeline_stack.py` looks like this: 

```
class PipelineStack(Stack):

  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    repository = "owner/repository"
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
```

In this file, replace `owner/repository` with your owner and repository name and `main` with your preferred branch name.  
Also, it looks for GitHub Personal Access Token stored in Secrets Manager, so make sure you store it in your AWS account.  


### 5. Create GitHub repository

To deploy your applicatoin, you need to have a GitHub repository.  
To do that, delete `.git` directory and push the contents to your newly created repository. Make sure repository and branch names match to the ones you specified in the previous steps. 


### 6. Deploy CDK application 

At this point, you should be able to deploy CDK application that creates CodePipeline pipeline to automate deployments of backend and frontend hosting resources as well as React web application.  
Before you do so, make sure your CDK stacks are defined properly by running following command: 

```
$ npx cdk synth
```

Once you confirmed everything looks good, deploy your applicatoin. Note that you do `cdk deploy` only once because changed made afer this step will be reflected by pipeline execution, therefore, all you need to do is push your change to the repository from the second time.

```
$ npx cdk deploy
```

After that, CodePipeline pipeline will be automatically created and defined resources will be deployed. 




