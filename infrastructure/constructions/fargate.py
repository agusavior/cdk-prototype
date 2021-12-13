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

#   ====================
#   CONFIGURE YOUR STACK
#   ====================

IMAGE_NAME = 'docker.io/nginx:latest'

# Put this in false if you don't want to have a custom domain
USE_CUSTOM_DOMAIN = False

if USE_CUSTOM_DOMAIN:
    # Put this in True if you want to use an existing Hosted Zone, outside of CDK and outside your Cloudformation Stack.
    # The Hosted Zone has to be in your account when you deploy this.
    USE_EXISTING_HOSTED_ZONE = False

    if USE_EXISTING_HOSTED_ZONE:
        # If you want to use an existing Hosted Zone, you must to complete this field.
        # Go to Route53, in Hosted Zones, and copy/paste your Hosted Zone ID.
        # 
        EXISTING_HOSTED_ZONE_ID = 'EXAMPLE1234567890000'

    if not USE_EXISTING_HOSTED_ZONE:
        # Put this in True if you want to create a new hosted zone when you build the stack.
        # If you create it, it will be attached to the stack. This means that, if you want to destroy
        # your entire stack, the hosted zone will be destroyed to.
        # If you'll put this in True, and you deploy, you should validate your Hosted Zone in order to finish the deploy;
        # to do this, follow the steps written in README.md
        CREATE_HOSTED_ZONE = False

        if CREATE_HOSTED_ZONE:
            # Do not use subdomains here. Put the entire domain name.
            DOMAIN_OF_HOSTED_ZONE = 'example.com'

            # Domain (with a subdomain if you want).
            DOMAIN_NAME = 'sub.example.tk'
    
    # Put this in True if you want to use HTTPS with your custom domain
    USE_HTTPS = True

    if USE_HTTPS:
        # Put this in True if you want to use an existing Certificate, outside of CDK and outside your Cloudformation Stack.
        # This Certificate must be created based on your custom domain.
        USE_EXISTING_CERTIFICATE = False
    


class Stack1(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TODO: Uncomment this!!
        return

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
        hosted_zone = route53.HostedZone(self, 'MyHostedZone', zone_name=DOMAIN_OF_HOSTED_ZONE)
        
        # route53.HostedZone.from_hosted_zone_id()

        # TODO: Use constants in this scope

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
    