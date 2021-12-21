#!/usr/bin/env python3
import os

import aws_cdk as cdk
import logging
from aws_cdk import Stack
from aws_cdk import (
    aws_ecr_assets as ecr_assets,
    aws_ecs as ecs,
    aws_ecr as ecr,
)
from aws_cdk.aws_ec2 import Vpc

from constructions.fargate import Stack1
from constructions.eb import ElasticBeanstalkConstruct, RUBY_SOLUTION_STACK_NAME
from constructions.domain import DomainConstruct
from constructions.ecs import EC2ProcessingConstruct

from stacks.domain import DomainStack
from stacks.ecs import ProcessingEC2ServiceStack
from stacks.vpc import VpcStack

CDK_DEFAULT_ACCOUNT = os.environ.get("CDK_DEFAULT_ACCOUNT")
CDK_DEFAULT_REGION = os.environ.get("CDK_DEFAULT_REGION")

IMAGE_NAME = 'docker.io/nginx:latest'

if not CDK_DEFAULT_REGION:
    raise AssertionError('CDK_DEFAULT_REGION must be defined.')

# =====================
# CLOUDFORMATION STACKS
# =====================
def define_stacks(app: cdk.App):
    # ============
    # DomainsStack
    # ============
    domains_stack = DomainStack(
        app,
        domain_of_hosted_zone='fanaty.com',
        sub_domain_list=[],
        existing_hosted_zone_id='Z1FHNQ1X01VLGA',
    )

    # ==========================================
    # ElasticBeanstalkStack Example Flask Server
    # Remember to run `python3 build.py` before deploy this stack.
    # ==========================================
    eb_flask_stack = Stack(app,
        id='eb-docker-flask',
        description='Elastic Beanstalk Stack for Example Flask Server'
    )
    ElasticBeanstalkConstruct(eb_flask_stack,
        id='example-flask-app',
        elb_zip_path='./build/example-flask-app.zip',
        instance_type_id='t3.small',
    )

    # =========
    # VPC Stack
    # =========
    vpc_stack = VpcStack(app, max_azs=3)

    # ==================
    # ECS for Processing
    # ==================
    image = ecs.ContainerImage.from_asset('../example-processing-app')
    # image = ecs.ContainerImage.from_registry('agusavior/ecs-processing-app:tagname')
    ecs_processing_stack = ProcessingEC2ServiceStack(
        app,
        id='ecs-processing',
        instance_type_id='t2.medium',
        image=image,
        vpc=vpc_stack.vpc,
    )
    
    # =========================
    # ElasticBeanstalkStack API
    # =========================
    eb_api_stack = Stack(app,
        id='stack4',
        description='Elastic Beanstalk Stack Ruby API'
    )
    ElasticBeanstalkConstruct(eb_api_stack,
        id='ruby-api',
        # elb_zip_path='../api/app.zip',
        elb_zip_path='./build/app-9c2e-210828_220249-downloaded.zip',
        solution_stack_name = RUBY_SOLUTION_STACK_NAME,
        instance_type_id='t2.medium',
    )

# =======
# CDK APP
# =======
app = cdk.App()
define_stacks(app)
app.synth()
