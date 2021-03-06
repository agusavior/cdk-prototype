from typing import Optional
from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_route53 as route53,
    aws_ecs_patterns as ecs_patterns,
    aws_certificatemanager as certificatemanager,
    aws_elasticbeanstalk as elasticbeanstalk,
    CfnOutput,
)
from aws_cdk.aws_ecr import Repository
from constructs import Construct

class EC2ProcessingConstruct(Construct):
    def __init__(
            self,
            scope: Construct,
            id: str,
            instance_type_id: str,                  # instance type
            image: ecs.ContainerImage,              # container image
            spot_price: Optional[str] = None,       # max spot price per hour. Example: '0.064'. If it is None, no spot instances are going to be used.
            max_azs: int = 3,                       # default is all AZs in region
            memory_mib=1024,                        # memory limit
            max_scaling_capacity=5,                 # maxim
        ) -> None:
        super().__init__(scope, id)

        vpc = ec2.Vpc(self, f'{id}-vpc', max_azs=max_azs)     

        cluster = ecs.Cluster(self, f'{id}-cluster', vpc=vpc)

        instance_type = ec2.InstanceType(instance_type_identifier=instance_type_id)

        # You can add more that one capacity
        cluster.add_capacity(f'{id}-capacity',
            instance_type=instance_type,
            spot_price=spot_price,
        )

        # Source: https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ecs-patterns.QueueProcessingEc2Service.html
        queue_processing_ec2_service = ecs_patterns.QueueProcessingEc2Service(self,
            id=id,
            cluster=cluster,
            # memory_limit_mib=memory_mib,
            memory_reservation_mib=memory_mib,
            image=image,
            # command=["-c", "4", "amazon.com"],  # Default: Uses the CMD of the image.
            enable_logging=True,
            environment={
                "TEST_ENVIRONMENT_VARIABLE1": "test environment variable 1 value",
                "TEST_ENVIRONMENT_VARIABLE2": "test environment variable 2 value"
            },
            max_scaling_capacity=max_scaling_capacity,
            container_name=f'{id}-container',
        )
