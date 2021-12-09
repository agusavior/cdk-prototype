from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_route53 as route53,
    aws-rds as rds,
    aws_ecs_patterns as ecs_patterns,
    aws_certificatemanager as certificatemanager,
    CfnOutput,
)
from constructs import Construct

IMAGE_NAME = 'docker.io/nginx:latest'
ZONE_NAME = 'agusavior.tk'
DOMAIN_NAME = 'lb.agusavior.tk'

class CdkPrototypeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # queue = sqs.Queue(
        #     self, "CdkPrototypeQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        vpc = ec2.Vpc(self, "MyVpc", max_azs=3)     # default is all AZs in region

        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        # DO NOT FORGET to set up the namespaces correctly once the zone name is created.
        # Go to your route53, open this zone, and copy the four namespaces.
        # Then, go to your domain provider and paste the namespaces in the configuration of the domain.
        hosted_zone = route53.HostedZone(self, 'MyHostedZone', zone_name=ZONE_NAME)
        
        certificate = certificatemanager.Certificate(self, 'MyCertificate',
            domain_name=DOMAIN_NAME,
            validation=certificatemanager.CertificateValidation.from_dns(hosted_zone),
            )

        ecs_patterns.ApplicationLoadBalancedFargateService(self, "MyFargateService",
            cluster=cluster,            # Required
            # cpu=512,                  # Default is 256
            # desired_count=1,          # Default is 1
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry(IMAGE_NAME)
            ),
            domain_name=DOMAIN_NAME,
            domain_zone=hosted_zone,
            certificate=certificate,
            redirect_http=True,
            # memory_limit_mib=2048,    # Default is 512
            public_load_balancer=True)  # Default is False
        
        CfnOutput(scope=self, id="certificate.certificate_arn", value=certificate.certificate_arn)
    