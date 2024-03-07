import pulumi
from pulumi_aws import ec2
import pulumi_aws as aws

class Platform:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.platform = {}
        self.numberOfZones = 2

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

            # Fetch available availability zones
            available_zones = aws.get_availability_zones(filters=[aws.GetAvailabilityZonesFilterArgs(
                name="opt-in-status",
                values=["opt-in-not-required"],
            )])

            # Assuming self.numberOfZones is defined somewhere in your class
            zones = [zone for zone in available_zones.names][:self.numberOfZones]

            # Create subnets in the specified number of availability zones
            for i, zone in enumerate(zones):
                # Public subnet
                public_subnet = ec2.Subnet(
                    f"{self.name}-public-{zone}",
                    vpc_id=vpc.id,
                    cidr_block=f"10.100.{i*2}.0/24",
                    availability_zone=zone,
                    map_public_ip_on_launch=True,
                    tags={
                        "Name": f"{self.name}-public-{zone}",
                    },
                    opts=pulumi.ResourceOptions(depends_on=[vpc])
                )

                # Private subnet
                private_subnet = ec2.Subnet(
                    f"{self.name}-private-{zone}",
                    vpc_id=vpc.id,
                    cidr_block=f"10.100.{i*2+1}.0/24",
                    availability_zone=zone,
                    map_public_ip_on_launch=False,
                    tags={
                        "Name": f"{self.name}-private-{zone}",
                    },
                    opts=pulumi.ResourceOptions(depends_on=[vpc])
                )

                # Export the subnet IDs within the loop
                pulumi.export(f"{zone}_public_subnet_id", public_subnet.id)
                pulumi.export(f"{zone}_private_subnet_id", private_subnet.id)
            
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
                subnet_id=public_subnet.id,  # Use the ID of the public subnet
                allocation_id=eip.id,
                tags={
                    "Name": f"{self.name}-nat-gateway",
                },
                opts=pulumi.ResourceOptions(depends_on=[vpc, eip])  # Ensure NAT Gateway depends on VPC and EIP
            )

        # Store references to the created resources
            self.platform["vpc"] = vpc
            self.platform["app_sg"] = app_sg
            self.platform["igw"] = igw
            self.platform[f"{zone}_public_subnet"] = public_subnet
            self.platform[f"{zone}_private_subnet"] = private_subnet
            self.platform["eip"] = eip
            self.platform["nat_gateway"] = nat_gateway

            # Export the VPC and Security Group IDs
            pulumi.export("vpc_id", vpc.id)
            pulumi.export("app_sg_id", app_sg.id)
            pulumi.export("igw_id", igw.id)
            pulumi.export("eip_id", eip.id)
            pulumi.export("nat_gateway_id", nat_gateway.id)
   

           
