import pulumi
from pulumi_aws import ec2
import pulumi_aws as aws
from network import create_vpc

class Platform:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.platform = {}
        self.zone1 = "ap-southeast-1a"
        self.zone2 = "ap-southeast-1b"

        if self.config.get("platform", {}).get("VPC", False):
            # Create VPC
            vpc = create_vpc(self.name, self.zone1, self.zone2)
                
            # Store references to the created network resources
            self.platform.update(vpc)

            # Export the VPC and Security Group IDs
            pulumi.export("vpc_id", self.platform["vpc"].id)
            pulumi.export("app_sg_id", self.platform["app_sg"].id)
            pulumi.export("igw_id", self.platform["igw"].id)
            pulumi.export("eip_id", self.platform["eip"].id)
            pulumi.export("nat_gateway_id", self.platform["nat_gateway"].id)
            pulumi.export(f"{self.name}-public-{self.zone1}", self.platform["public_subnet_zone1"].id)
            pulumi.export(f"{self.name}-private-{self.zone1}", self.platform["private_subnet_zone1"].id)
            pulumi.export(f"{self.name}-public-{self.zone2}", self.platform["public_subnet_zone2"].id)
            pulumi.export(f"{self.name}-private-{self.zone2}", self.platform["private_subnet_zone2"].id)




   

           
