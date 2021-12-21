from typing import List, Optional
from attr import validate
from aws_cdk import (
    Duration,
    Stack,
    aws_elasticbeanstalk as elasticbeanstalk,
    aws_route53_targets as targets,
    aws_s3_assets as s3_assets,
    CfnOutput,
    aws_route53 as route53,
)
import aws_cdk
from constructs import Construct
import os

# I've been guided by this article:
# https://medium.com/@joshmustill/complete-node-js-aws-elastic-beanstalk-application-packaging-through-cdk-in-typescript-e91b7ffe4928

# I don't know what is this and if you can put any string in here.
# https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-solutionstackname
# https://docs.aws.amazon.com/elasticbeanstalk/latest/platforms/platforms-supported.html
DOCKER_SOLUTION_STACK_NAME = '64bit Amazon Linux 2 v3.4.9 running Docker'
RUBY_SOLUTION_STACK_NAME = '64bit Amazon Linux 2 v3.4.0 running Ruby 2.6'

# Shortcut
OptionSettingProperty = elasticbeanstalk.CfnEnvironment.OptionSettingProperty

# This construct creates another Stack, like a companion Stack
class ElasticBeanstalkConstruct(Construct):
    class DomainConfiguration:
        def __init__(
                self,
                region: str,                            # Example: 'eu-central-1'
                domain_name: str,                       # Example: 'foo.example.com'
                hosted_zone: route53.IHostedZone,       # The Hosted Zone of the domain_name (Example: example.com)
                arn_certificate: Optional[str] = None,  # ARN Certificate, of Certificates Manager, of the domain domain_name
            ) -> None:
            self.region = region
            self.hosted_zone = hosted_zone
            self.domain_name = domain_name
            self.arn_certificate = arn_certificate
    
    def __init__(
            self,
            scope: Construct,
            id: str,
            elb_zip_path: str,                                # Create a zip with all the project content before deploy this
            instance_type_id: Optional[str],                  # Exampe: 't2.medium'
            domain_configuration: Optional[DomainConfiguration] = None,
            solution_stack_name = DOCKER_SOLUTION_STACK_NAME,
        ) -> None:
        super().__init__(scope, id)

        # Attributes
        self.domain_configuration = domain_configuration
        self.instance_type_id = instance_type_id

        elb_zip_archive = s3_assets.Asset(self, f'{id}Zip', path=elb_zip_path)
        
        # EB Application
        application_name = f'{id}-app'
        application_id = f'{id}-app'
        application = elasticbeanstalk.CfnApplication(
            self,
            id=application_id,
            application_name=application_name
        )

        # Create an app version from the S3 asset defined above
        # The S3 "putObject" will occur first before CF generates the template
        app_version_props = elasticbeanstalk.CfnApplicationVersion(self, 'AppVersion', 
            application_name=application_name,
            source_bundle=elasticbeanstalk.CfnApplicationVersion.SourceBundleProperty(
                s3_bucket=elb_zip_archive.s3_bucket_name,
                s3_key=elb_zip_archive.s3_object_key,
            )
        )

        # EB Enviroment
        # This enviroment will launch another Cloudformation template in order to deploy its own stack.
        # So, each enviroment of this has associeated a entire Cloudformation stack.
        environment_name = f'{id}-env'
        applicatoin_id = f'{id}-env'
        enviroment = elasticbeanstalk.CfnEnvironment(self, applicatoin_id, 
            environment_name=environment_name,
            application_name=application.application_name or application_name,
            solution_stack_name=solution_stack_name,
            option_settings=self.get_option_setting_properties(),
            # This line is critical - reference the label created in this same stack
            version_label=app_version_props.ref,
        )

        # Also important - make sure that `app` exists before creating an app version
        app_version_props.add_depends_on(application)

        CfnOutput(self, 's3_bucket_name', value=elb_zip_archive.s3_bucket_name)
        CfnOutput(self, 'attr_endpoint_url', value=enviroment.attr_endpoint_url)
        
    # About options: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-option-settings.html
    # And: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/command-options.html
    def get_option_setting_properties(self) -> List[OptionSettingProperty]:
        options: List[OptionSettingProperty] = []

        options.append(
            OptionSettingProperty(
                namespace='aws:autoscaling:launchconfiguration',
                option_name='IamInstanceProfile',
                # Here you could reference an instance profile by ARN (e.g. myIamInstanceProfile.attrArn)
                # For the default setup, leave this as is (it is assumed this role exists)
                # https://stackoverflow.com/a/55033663/6894670
                value='aws-elasticbeanstalk-ec2-role',
            ),
        )

        # Instace type
        if self.instance_type_id:
            options.append(
                OptionSettingProperty(
                    namespace='aws:autoscaling:launchconfiguration',
                    option_name='InstanceType',
                    value=self.instance_type_id,
                ),
            )

        return options
    