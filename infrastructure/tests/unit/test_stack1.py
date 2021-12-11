import aws_cdk as core
import aws_cdk.assertions as assertions

from stacks.stack1 import Stack1

# example tests. To run these tests, uncomment this file along with the example
# resource in stacks/stack1.py
def test_sqs_queue_created():
    app = core.App()
    stack = Stack1(app, 'stack1')
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
