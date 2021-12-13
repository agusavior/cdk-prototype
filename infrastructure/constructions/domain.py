from typing import Dict, List, Optional
from constructs import Construct

from aws_cdk import (
    aws_route53 as route53,
    aws_certificatemanager as certificatemanager,
    CfnOutput,
)

class DomainConstruct(Construct):
    OUTPUT_CERTIFICATE_ARNS = True

    def __init__(
        self,
        scope: Construct,                                   # The parent Construct or Stack
        domain_of_hosted_zone: str,                         # Example: 'example.com'
        sub_domain_list: List[str] = [],                    # Example: ['sub.example.com', 'foo.example.com']
        existing_hosted_zone_id: Optional[str] = None,      # Fill this field if you don't want to create an new Hosted Zone.
    ) -> None:
        super().__init__(scope, f'{domain_of_hosted_zone}Construct')

        # Construct an Id for the Hosted Zone
        hosted_zone_id = f'HostedZone{domain_of_hosted_zone}'
        
        # Assert that every sub domain ends correctly
        for sub_domain in sub_domain_list:
            assert sub_domain.endswith(domain_of_hosted_zone)

        if existing_hosted_zone_id:
            hosted_zone = route53.HostedZone.from_hosted_zone_id(
                self,
                id=hosted_zone_id,
                hosted_zone_id=existing_hosted_zone_id
            )
        else:
            # DO NOT FORGET to set up the namespaces correctly once the zone name is created.
            # Go to your route53, open this zone, and copy the four namespaces.
            # Then, go to your domain provider and paste the namespaces in the configuration of the domain.    
            hosted_zone = route53.HostedZone(
                self,
                id=hosted_zone_id,
                zone_name=domain_of_hosted_zone
            )

        # Add a certificate for each sub domain
        certificate_of: Dict[str, certificatemanager.Certificate] = dict()
        for sub_domain in sub_domain_list:
            certificate = certificatemanager.Certificate(self, f'CertificateOf{sub_domain}',
                domain_name=sub_domain,
                validation=certificatemanager.CertificateValidation.from_dns(hosted_zone),
                )
            
            if self.OUTPUT_CERTIFICATE_ARNS:
                CfnOutput(self, id=f'certificate_arn_of_{sub_domain}', value= certificate.certificate_arn)
        
        # Store some properties in the instance
        self.hosted_zone = hosted_zone
        self.certificate_of = certificate_of
