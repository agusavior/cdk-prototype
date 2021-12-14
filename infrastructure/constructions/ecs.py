from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_route53 as route53,
    aws_ecs_patterns as ecs_patterns,
    aws_certificatemanager as certificatemanager,
    aws_elasticbeanstalk as elasticbeanstalk,
    CfnOutput,
)
from constructs import Construct

class ECSConstruct(Construct):
    def __init__(
            self,
            scope: Construct,
            construct_label: str,
            image_name: str,            # for instance: 'docker.io/nginx:latest'
            spot: bool,                 # use or not EC2 Spot
            max_azs: int = 3,           # default is all AZs in region
            memory_limit_mib=1024,      # memory limit
        ) -> None:
        super().__init__(scope, f'{construct_label}Construct')

        vpc = ec2.Vpc(self, f'{construct_label}Vpc', max_azs=max_azs)     

        cluster = ecs.Cluster(self, '{construct_label}Cluster', vpc=vpc)

        # Source: https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ecs-patterns.QueueProcessingEc2Service.html
        queue_processing_ec2_service = ecs_patterns.QueueProcessingEc2Service(self, id=f'{construct_label}QueueProcessingEc2Service',
            cluster=cluster,
            memory_limit_mib=memory_limit_mib,
            image=ecs.ContainerImage.from_registry(image_name),
            # command=["-c", "4", "amazon.com"],  # Default: Uses the CMD of the image.
            enable_logging=False,
            environment={
                "TEST_ENVIRONMENT_VARIABLE1": "test environment variable 1 value",
                "TEST_ENVIRONMENT_VARIABLE2": "test environment variable 2 value"
            },
            max_scaling_capacity=5,
            container_name=f'{construct_label}Container'
        )

        