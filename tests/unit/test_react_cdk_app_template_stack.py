import aws_cdk as core
import aws_cdk.assertions as assertions

from react_cdk_app_template.react_cdk_app_template_stack import ReactCdkAppTemplateStack

# example tests. To run these tests, uncomment this file along with the example
# resource in react_cdk_app_template/react_cdk_app_template_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ReactCdkAppTemplateStack(app, "react-cdk-app-template")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
