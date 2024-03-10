import pulumi
from pulumi_aws import ec2
import pulumi_aws as aws

class Platform:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.platform = {}
        self.zone1 = "ap-southeast-1a"
        self.zone2 = "ap-southeast-1b"

        if self.config.get("platform", {}).get("VPC", False):
            # Create a VPC
            vpc = ec2.Vpc(
                f"{self.name}-vpc",
                cidr_block="10.100.0.0/16",
                enable_dns_support=True,
                enable_dns_hostnames=True,
                instance_tenancy="default",
                tags={
                    "Name": f"{self.name}-vpc",
                },
            )

            # Create an Internet Gateway and attach it to the VPC
            igw = ec2.InternetGateway(
                f"{self.name}-igw",
                vpc_id=vpc.id,
                tags={
                    "Name": f"{self.name}-igw",
                },
            )

            # Create public and private subnets in each specified availability zone
            # Public Subnet in Zone 1
            public_subnet_zone1 = ec2.Subnet(
                f"{self.name}-public-{self.zone1}",
                vpc_id=vpc.id,
                cidr_block="10.100.0.0/24",
                availability_zone=self.zone1,
                map_public_ip_on_launch=True,
                tags={
                    "Name": f"{self.name}-public-{self.zone1}",
                },
                opts=pulumi.ResourceOptions(depends_on=[vpc])
            )

            # Private Subnet in Zone 1
            private_subnet_zone1 = ec2.Subnet(
                f"{self.name}-private-{self.zone1}",
                vpc_id=vpc.id,
                cidr_block="10.100.1.0/24",
                availability_zone=self.zone1,
                map_public_ip_on_launch=False,
                tags={
                    "Name": f"{self.name}-private-{self.zone1}",
                },
                opts=pulumi.ResourceOptions(depends_on=[vpc])
            )

            # Public Subnet in Zone 2
            public_subnet_zone2 = ec2.Subnet(
                f"{self.name}-public-{self.zone2}",
                vpc_id=vpc.id,
                cidr_block="10.100.2.0/24",
                availability_zone=self.zone2,
                map_public_ip_on_launch=True,
                tags={
                    "Name": f"{self.name}-public-{self.zone2}",
                },
                opts=pulumi.ResourceOptions(depends_on=[vpc])
            )

            # Private Subnet in Zone 2
            private_subnet_zone2 = ec2.Subnet(
                f"{self.name}-private-{self.zone2}",
                vpc_id=vpc.id,
                cidr_block="10.100.3.0/24",
                availability_zone=self.zone2,
                map_public_ip_on_launch=False,
                tags={
                    "Name": f"{self.name}-private-{self.zone2}",
                },
                opts=pulumi.ResourceOptions(depends_on=[vpc])
            )

            # Create Security Groups
            app_sg = ec2.SecurityGroup(
                f"{self.name}-app-sg",
                vpc_id=vpc.id,
                description="Application Security Group",
                ingress=[
                    {
                        "protocol": "tcp",
                        "from_port": 80,
                        "to_port": 80,
                        "cidr_blocks": ["0.0.0.0/0"],
                        "description": "Allow HTTP",
                    },
                    {
                        "protocol": "tcp",
                        "from_port": 443,
                        "to_port": 443,
                        "cidr_blocks": ["0.0.0.0/0"],
                        "description": "Allow HTTPS",
                    },
                    {
                        "protocol": "tcp",
                        "from_port": 22,
                        "to_port": 22,
                        "cidr_blocks": ["0.0.0.0/0"],
                        "ipv6_cidr_blocks": ["::/0"],
                        "description": "SSH Access",
                    },
                    {
                        "protocol": "tcp",
                        "from_port": 8080,
                        "to_port": 8080,
                        "cidr_blocks": ["0.0.0.0/0"],
                        "ipv6_cidr_blocks": ["::/0"],
                        "description": "Jenkins",
                    },
                    {
                        "protocol": "tcp",
                        "from_port": 9000,
                        "to_port": 9000,
                        "cidr_blocks": ["0.0.0.0/0"],
                        "ipv6_cidr_blocks": ["::/0"],
                        "description": "SonarQube",
                    },
                    {
                        "protocol": "tcp",
                        "from_port": 9090,
                        "to_port": 9090,
                        "cidr_blocks": ["0.0.0.0/0"],
                        "ipv6_cidr_blocks": ["::/0"],
                        "description": "Custom Application",
                    },
                ],
                egress=[
                    {
                        "protocol": "-1",
                        "from_port": 0,
                        "to_port": 0,
                        "cidr_blocks": ["0.0.0.0/0"],
                        "ipv6_cidr_blocks": ["::/0"],
                    }
                ],
                tags={
                    "Name": f"{self.name}-app-sg",
                },
                opts=pulumi.ResourceOptions(depends_on=[vpc])
            )

            # Allocate an Elastic IP for the NAT Gateway
            eip = aws.ec2.Eip(f"{self.name}-eip", vpc=True)

            # Assuming you have a public subnet created and its ID is stored in `public_subnet_id`
            # Replace `public_subnet_id` with the actual variable or method that retrieves your public subnet ID
            nat_gateway = aws.ec2.NatGateway(
                f"{self.name}-nat-gateway",
                subnet_id=public_subnet_zone1.id,  # Use the ID of the public subnet
                allocation_id=eip.id,
                tags={
                    "Name": f"{self.name}-nat-gateway",
                },
                opts=pulumi.ResourceOptions(depends_on=[vpc, eip])  # Ensure NAT Gateway depends on VPC and EIP
            )

            # Store references to the created resources
            self.platform = {
                "vpc": vpc,
                "app_sg": app_sg,
                "igw": igw,
                "eip": eip,
                "nat_gateway": nat_gateway,
                "public_subnet_zone1": public_subnet_zone1,
                "private_subnet_zone1": private_subnet_zone1,
                "public_subnet_zone2": public_subnet_zone2,
                "private_subnet_zone2": private_subnet_zone2
            }

            # Export the VPC and Security Group IDs
            pulumi.export("vpc_id", vpc.id)
            pulumi.export("app_sg_id", app_sg.id)
            pulumi.export("igw_id", igw.id)
            pulumi.export("eip_id", eip.id)
            pulumi.export("nat_gateway_id", nat_gateway.id)
            pulumi.export(f"{self.name}-public-{self.zone1}", public_subnet_zone1.id)
            pulumi.export(f"{self.name}-private-{self.zone1}", private_subnet_zone1.id)
            pulumi.export(f"{self.name}-public-{self.zone2}", public_subnet_zone2.id)
            pulumi.export(f"{self.name}-private-{self.zone2}", private_subnet_zone2.id)




   

           
