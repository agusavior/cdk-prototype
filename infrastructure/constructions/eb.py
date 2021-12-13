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
SOLUTION_STACK_NAME = '64bit Amazon Linux 2 v3.4.9 running Docker'

# Shortcut
OptionSettingProperty = elasticbeanstalk.CfnEnvironment.OptionSettingProperty

# Source:
# https://stackoverflow.com/questions/56164141/aws-cdk-how-to-target-an-elastic-beanstalk-environment-with-a-route53-alias-rec 
# https://docs.aws.amazon.com/general/latest/gr/elb.html
ELB_ZONE_IDS = {
    'us-east-2': 'Z3AADJGX6KTTL2',
    'us-east-1': 'Z368ELLRRE2KJ0',
    'us-west-1': 'Z368ELLRRE2KJ0',
    'us-west-2': 'Z1H1FL5HABSF5',
    'af-south-1': 'Z268VQBMOI5EKX',
    'ap-east-1': 'Z3DQVH9N71FHZ0',
    'ap-south-1': 'ZP97RAFLXTNZK',
    'ap-northeast-3': 'Z5LXEXXYW11ES',
    'ap-northeast-2': 'ZWKZPGTI48KDX',
    'ap-southeast-1': 'Z1LMS91P8CMLE5',
    'ap-southeast-2': 'Z1GM3OXH4ZPM65',
    'ap-northeast-1': 'Z14GRHDCWA56QT',
    'ca-central-1': 'ZQSVJUPU6J1EY',
    'cn-north-1': 'Z1GDH35T77C1KE',
    'cn-northwest-1': 'ZM7IZAIOVVDZF',
    'eu-central-1': 'Z215JYRZR1TBD5',
    'eu-west-1': 'Z32O12XQLNTSW2',
    'eu-west-2': 'ZHURV8PSTC4K8',
    'eu-south-1': 'Z3ULH7SSC9OV64',
    'eu-west-3': 'Z3Q77PNBQS71R4',
    'eu-north-1': 'Z23TAZ6LKFMNIO',
    'me-south-1': 'ZS929ML54UICD',
    'sa-east-1': 'Z2P70J7HTTTPLU',
    'us-gov-east-1': 'Z166TLBEWOO7G0',
    'us-gov-west-1': 'Z33AYJ8TM3BH4J',
}

# Helper to generate a instance of type IAliasRecordTarget
def generate_elb_alias_record_target(dns_name: str, region: str) -> route53.IAliasRecordTarget:
    import jsii
    #@jsii.implements(route53.IAliasRecordTarget)
    class ELBAliasRecordTarget(route53.IAliasRecordTarget):
        def bind(self, record: route53.IRecordSet, zone: Optional[route53.IHostedZone] = None) -> route53.AliasRecordTargetConfig:
            return route53.AliasRecordTargetConfig(
                dns_name=dns_name,
                hosted_zone_id=ELB_ZONE_IDS[region],
            )
    return ELBAliasRecordTarget


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
            elb_zip_path: str,
            construct_label: str = 'ElasticBeanstalk',
            domain_configuration: Optional[DomainConfiguration] = None,
        ) -> None:
        super().__init__(scope, f'{construct_label}Construct')

        # Attributes
        self.domain_configuration = domain_configuration

        elb_zip_archive = s3_assets.Asset(self, f'{construct_label}Zip', path=elb_zip_path)
        
        # EB Application
        application_name = f'{construct_label}App'
        application_id = f'{application_name}AppId'
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
        environment_name = f'{construct_label}Enviroment'
        applicatoin_id = f'{construct_label}EnviromentId'
        enviroment = elasticbeanstalk.CfnEnvironment(self, applicatoin_id, 
            environment_name=environment_name,
            application_name=application.application_name or application_name,
            solution_stack_name=SOLUTION_STACK_NAME,
            option_settings=self.get_option_setting_properties(),
            # This line is critical - reference the label created in this same stack
            version_label=app_version_props.ref,
        )

        # Also important - make sure that `app` exists before creating an app version
        app_version_props.add_depends_on(application)

        # Domain attachment
        # TODO: Remove the 'False' once this issue finished: https://github.com/aws/aws-cdk/issues/17992
        if False and domain_configuration:
            # Attach Domain to DNS Domain of the Load Balancer of the Enviroment
            a_record = route53.ARecord(self, f'{construct_label}AliasRecord',
                target=route53.RecordTarget.from_alias(
                    targets.ElasticBeanstalkEnvironmentEndpointTarget(
                        enviroment.attr_endpoint_url,
                    ),
                ),
                zone=domain_configuration.hosted_zone,
            )

        CfnOutput(self, 'elb_zip_archive.s3_bucket_name', value=elb_zip_archive.s3_bucket_name)
        CfnOutput(self, 'enviroment.attr_endpoint_url', value=enviroment.attr_endpoint_url)

    # About options: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-beanstalk-option-settings.html
    # And: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/command-options.html
    def get_option_setting_properties(self) -> List[OptionSettingProperty]:
        options: List[OptionSettingProperty] = []

        options.extend([
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
        ])

        # If there is domain_configuration, set up HTTPS
        domain_configuration = self.domain_configuration
        if domain_configuration and domain_configuration.arn_certificate:
            arn_certificate = domain_configuration.arn_certificate

            # Let's set up HTTPs
            options.append(OptionSettingProperty(
                namespace='aws:elb:listener:listener_port',
                option_name='ListenerProtocol',
                value='HTTPS',
            ))

            # Certificate
            options.append(OptionSettingProperty(
                namespace='aws:elb:listener:listener_port',
                option_name='SSLCertificateId',
                value=arn_certificate,
            ))

        return options
    