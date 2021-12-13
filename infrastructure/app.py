#!/usr/bin/env python3
import os

import aws_cdk as cdk
from aws_cdk import Stack

from constructions.fargate import Stack1
from constructions.eb import ElasticBeanstalkConstruct
from constructions.domain import DomainConstruct

CDK_DEFAULT_ACCOUNT = os.environ.get("CDK_DEFAULT_ACCOUNT")
CDK_DEFAULT_REGION = os.environ.get("CDK_DEFAULT_REGION")

if not CDK_DEFAULT_REGION:
    raise AssertionError('CDK_DEFAULT_REGION must be defined.')

# =====================
# CLOUDFORMATION STACKS
# =====================
def define_stacks(app: cdk.App):
    # ============
    # DomainsStack
    # Each time this comes up, it costs like 0.5 USD. So, take care.
    # This is because when you turn on a new HostedZone, it costs 0.5 USD.
    # You can select which Stacks you want to deploy or destroy being specific in your commands,
    # for instance, you can do: `cdk destroy Stack1`.
    # ============
    domains_stack = Stack(app, 'DomainsStack',
        description='The Stack that contains Hosted Zones, certificates, and so.'
    )

    # Attach a DomainConstruct in the Stack
    domain = DomainConstruct(
        domains_stack,
        domain_of_hosted_zone='agusavior.tk',
        sub_domain_list=['eb.agusavior.tk'],
    )

    stack1 = Stack(app, id='Stack1',
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

    # =====================
    # ElasticBeanstalkStack
    # =====================
    eb_stack = Stack(app, id='Stack2', description='Elastic Beanstalk Stack')
    ElasticBeanstalkConstruct(eb_stack,
        elb_zip_path='./build/app.zip',
        domain_configuration=ElasticBeanstalkConstruct.DomainConfiguration(
            region=CDK_DEFAULT_REGION,
            domain_name='eb.agusavior.tk',
            hosted_zone=domain.hosted_zone,
        )
    )

# =======
# CDK APP
# =======
app = cdk.App()
define_stacks(app)
app.synth()
