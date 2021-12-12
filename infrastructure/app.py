#!/usr/bin/env python3
import os

import aws_cdk as cdk

from applications.fargate import Stack1
from applications.eb import Stack2

CDK_DEFAULT_ACCOUNT = os.environ.get("CDK_DEFAULT_ACCOUNT")
CDK_DEFAULT_REGION = os.environ.get("CDK_DEFAULT_REGION")

# ==========
# CDK APP (INFRASTRUCTURE OF EACH APP)
# ==========

app = cdk.App()
Stack1(app, 'Stack1',
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )

# Beanstalk stack
Stack2(app, 'Stack2')

app.synth()
