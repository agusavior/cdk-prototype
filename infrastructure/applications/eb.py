from typing import List
from attr import validate
from aws_cdk import (
    Duration,
    Stack,
    aws_elasticbeanstalk as elasticbeanstalk,
    aws_s3_assets as s3_assets,
    CfnOutput,
)
from constructs import Construct
import os

# I've been guided by this article:
# https://medium.com/@joshmustill/complete-node-js-aws-elastic-beanstalk-application-packaging-through-cdk-in-typescript-e91b7ffe4928

# I don't know what is this
# https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-environment.html#cfn-beanstalk-environment-solutionstackname
# https://docs.aws.amazon.com/elasticbeanstalk/latest/platforms/platforms-supported.html
SOLUTION_STACK_NAME = '64bit Amazon Linux 2 v3.4.9 running Docker'

# Shortcut
OptionSettingProperty = elasticbeanstalk.CfnEnvironment.OptionSettingProperty

class Stack2(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        elb_zip_archive = s3_assets.Asset(self, 'MyElbAppZip', path='./build/app.zip')
        
        application_name = 'MyApp'
        application = elasticbeanstalk.CfnApplication(self, 'Application', application_name=application_name)

        # Create an app version from the S3 asset defined above
        # The S3 "putObject" will occur first before CF generates the template
        app_version_props = elasticbeanstalk.CfnApplicationVersion(self, 'AppVersion', 
            application_name=application_name,
            source_bundle=elasticbeanstalk.CfnApplicationVersion.SourceBundleProperty(
                s3_bucket=elb_zip_archive.s3_bucket_name,
                s3_key=elb_zip_archive.s3_object_key,
            )
        )

        enviroment = elasticbeanstalk.CfnEnvironment(self, 'Enviroment', 
            environment_name='MySampleEnviroment',
            application_name=application.application_name or application_name,
            solution_stack_name=SOLUTION_STACK_NAME,
            option_settings=self.get_option_setting_properties(),
            # This line is critical - reference the label created in this same stack
            version_label=app_version_props.ref,
        )

        # Also important - make sure that `app` exists before creating an app version
        app_version_props.add_depends_on(application)

        CfnOutput(self, 'elb_zip_archive.s3_bucket_name', value=elb_zip_archive.s3_bucket_name)
        CfnOutput(self, 'enviroment.attr_endpoint_url', value=enviroment.attr_endpoint_url)

    # About options: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-option-settings.html
    def get_option_setting_properties(self) -> List[OptionSettingProperty]:
        return [
            OptionSettingProperty(
                namespace='aws:autoscaling:launchconfiguration',
                option_name='InstanceType',
                value='t3.small',
            ),
            OptionSettingProperty(
                namespace='aws:autoscaling:launchconfiguration',
                option_name='IamInstanceProfile',
                # Here you could reference an instance profile by ARN (e.g. myIamInstanceProfile.attrArn)
                # For the default setup, leave this as is (it is assumed this role exists)
                # https://stackoverflow.com/a/55033663/6894670
                value='aws-elasticbeanstalk-ec2-role',
            ),
            # I think this isn't neccesary:  TODO: Delete this if it works
            # OptionSettingProperty(
            #     namespace='aws:elasticbeanstalk:container:python',
            #     option_name='',
            #     value=''
            # )
        ]
    