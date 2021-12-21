from typing import Dict, List, Optional
from constructs import Construct

from aws_cdk import (
    Stack,
    aws_route53 as route53,
    aws_certificatemanager as certificatemanager,
    CfnOutput,
)

class DomainStack(Stack):
    def __init__(
        self,
        scope: Construct,
        domain_of_hosted_zone: str,                     # Example: 'example.com'
        sub_domain_list: List[str] = [],                # Example: ['sub.example.com', 'foo.example.com']
        existing_hosted_zone_id: Optional[str] = None,  # Fill this field if you don't want to create an new Hosted Zone. Read warning below.
    ) -> None:
        # Replace 'example.com' for 'example-dot-com'
        id = domain_of_hosted_zone.replace('.', '-dot-')

        # Join all domains
        all_domains = [domain_of_hosted_zone, ] + sub_domain_list

        # Call super constructor
        super().__init__(
            scope=scope,
            id=id,
            description=f'Hosted zone and certificates of {", ".join(all_domains)}.'
        )

        # Warning: Each time a Hosted Zone is created, it costs like 0.5 USD. So, take care.
        # Also, very important, each time you create a Hosted Zone with CDK, the deploy will stops until you
        # attach the namespaces to your domain. Do do it, first deploy, and then, go to your route53
        # open the hosted zone created, and copy the four namespaces.
        # Then, go to your domain provider and paste the namespaces in the configuration of the domain.
        
        # Assert that every sub domain ends correctly
        for sub_domain in sub_domain_list:
            assert sub_domain.endswith(domain_of_hosted_zone)

        if existing_hosted_zone_id:
            hosted_zone = route53.HostedZone.from_hosted_zone_id(
                self,
                id=id,
                hosted_zone_id=existing_hosted_zone_id
            )
        else:
            # Do not forget to set up the namespaces correctly once the zone name is created.

            hosted_zone = route53.HostedZone(
                self,
                id=id,
                zone_name=domain_of_hosted_zone
            )

        # Store some properties in the instance
        self.hosted_zone = hosted_zone
        self._certificates = self.generate_certificates(all_domains, hosted_zone)
    
    def generate_certificates(self, all_domains, hosted_zone) -> Dict[str, certificatemanager.Certificate]:
        # Add a certificate for the domain and each sub domain
        certificates: Dict[str, certificatemanager.Certificate] = dict()
        for sub_domain in all_domains:
            certificate = certificatemanager.Certificate(self,
                id=sub_domain,
                domain_name=sub_domain,
                validation=certificatemanager.CertificateValidation.from_dns(hosted_zone),
            )
            
            CfnOutput(self, id=f'certificate_arn_of_{sub_domain}', value= certificate.certificate_arn)

        return certificates

    def get_certificate_of(self, domain_or_sub_domain: str) -> certificatemanager.Certificate:
        if domain_or_sub_domain not in self._certificates:
            raise Exception('You are using get_certificate_of over an non declared domain neighter subdomain.')
        
        return self._certificates[domain_or_sub_domain]

# Interface.
class IDomainAttachable:
    def attach_to_domain(
        self,
        domain_stack: DomainStack,
        domain: str # Example: 'foo.example.com'
        ):
        raise NotImplementedError()
