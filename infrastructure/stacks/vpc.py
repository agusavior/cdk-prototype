from typing import Optional
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

class VpcStack(Stack):
    def __init__(
            self,
            scope: Construct,
            max_azs: Optional[int] = 3,     # default is all AZs in region
        ) -> None:
        super().__init__(
            scope,
            id='vpc-stack',
            description='Stack that holds the VPCs.'
        )

        self.vpc = ec2.Vpc(self, f'vpc-stack-vpc', max_azs=max_azs)     
