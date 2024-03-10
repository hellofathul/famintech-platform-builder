import pulumi
from pulumi_aws import ec2
import pulumi_aws as aws

def create_vpc(name, zone1, zone2):
    resources = {}

    # Create a VPC
    vpc = ec2.Vpc(
        f"{name}-vpc",
        cidr_block="10.100.0.0/16",
        enable_dns_support=True,
        enable_dns_hostnames=True,
        instance_tenancy="default",
        tags={
            "Name": f"{name}-vpc",
        },
    )

    # Create an Internet Gateway and attach it to the VPC
    igw = ec2.InternetGateway(
        f"{name}-igw",
        vpc_id=vpc.id,
        tags={
            "Name": f"{name}-igw",
        },
        opts=pulumi.ResourceOptions(depends_on=[vpc])
    )

    # Create public and private subnets in each specified availability zone
    # Public Subnet in Zone 1
    public_subnet_zone1 = ec2.Subnet(
        f"{name}-public-{zone1}",
        vpc_id=vpc.id,
        cidr_block="10.100.0.0/24",
        availability_zone=zone1,
        map_public_ip_on_launch=True,
        tags={
            "Name": f"{name}-public-{zone1}",
        },
        opts=pulumi.ResourceOptions(depends_on=[vpc])
    )

    # Private Subnet in Zone 1
    private_subnet_zone1 = ec2.Subnet(
        f"{name}-private-{zone1}",
        vpc_id=vpc.id,
        cidr_block="10.100.1.0/24",
        availability_zone=zone1,
        map_public_ip_on_launch=False,
        tags={
            "Name": f"{name}-private-{zone1}",
        },
        opts=pulumi.ResourceOptions(depends_on=[vpc])
    )

    # Public Subnet in Zone 2
    public_subnet_zone2 = ec2.Subnet(
        f"{name}-public-{zone2}",
        vpc_id=vpc.id,
        cidr_block="10.100.2.0/24",
        availability_zone=zone2,
        map_public_ip_on_launch=True,
        tags={
            "Name": f"{name}-public-{zone2}",
        },
        opts=pulumi.ResourceOptions(depends_on=[vpc])
    )

    # Private Subnet in Zone 2
    private_subnet_zone2 = ec2.Subnet(
        f"{name}-private-{zone2}",
        vpc_id=vpc.id,
        cidr_block="10.100.3.0/24",
        availability_zone=zone2,
        map_public_ip_on_launch=False,
        tags={
            "Name": f"{name}-private-{zone2}",
        },
        opts=pulumi.ResourceOptions(depends_on=[vpc])
    )

    # Create a Route Table for the public subnet
    public_route_table_zone1 = ec2.RouteTable(
        f"{name}-public-{zone1}-route-table",
        vpc_id=vpc.id,
        tags={
            "Name": f"{name}-public-{zone1}-route-table",
        },
        opts=pulumi.ResourceOptions(depends_on=[vpc])
    )

    # Create a route in the Route Table that directs internet-bound traffic to the Internet Gateway
    public_internet_route_zone1 = ec2.Route(
        f"{name}-public-{zone1}-internet-route",
        destination_cidr_block="0.0.0.0/0",
        gateway_id=igw.id,
        route_table_id=public_route_table_zone1.id,
        opts=pulumi.ResourceOptions(depends_on=[igw, public_route_table_zone1])
    )

    # Associate the public subnet with the Route Table
    public_route_table_association_zone1 = ec2.RouteTableAssociation(
        f"{name}-public-{zone1}-route-table-association",
        subnet_id=public_subnet_zone1.id,
        route_table_id=public_route_table_zone1.id,
        opts=pulumi.ResourceOptions(depends_on=[public_subnet_zone1, public_route_table_zone1])
    )

    # Create a Route Table for the public subnet
    private_route_table_zone1 = ec2.RouteTable(
        f"{name}-private-{zone1}-route-table",
        vpc_id=vpc.id,
        tags={
            "Name": f"{name}-private-{zone1}-route-table",
        },
        opts=pulumi.ResourceOptions(depends_on=[vpc])
    )

    # Associate the public subnet with the Route Table
    private_route_table_association_zone1 = ec2.RouteTableAssociation(
        f"{name}-private-{zone1}-route-table-association",
        subnet_id=private_subnet_zone1.id,
        route_table_id=private_route_table_zone1.id,
        opts=pulumi.ResourceOptions(depends_on=[private_subnet_zone1, private_route_table_zone1])
    )

    # Create a Route Table for the public subnet
    public_route_table_zone2 = ec2.RouteTable(
        f"{name}-public-{zone2}-route-table",
        vpc_id=vpc.id,
        tags={
            "Name": f"{name}-public-{zone2}-route-table",
        },
        opts=pulumi.ResourceOptions(depends_on=[vpc])
    )

    # Create a route in the Route Table that directs internet-bound traffic to the Internet Gateway
    public_internet_route_zone2 = ec2.Route(
        f"{name}-public-{zone2}-internet-route",
        destination_cidr_block="0.0.0.0/0",
        gateway_id=igw.id,
        route_table_id=public_route_table_zone2.id,
        opts=pulumi.ResourceOptions(depends_on=[igw, public_route_table_zone2])
    )

    # Associate the public subnet with the Route Table
    public_route_table_association_zone2 = ec2.RouteTableAssociation(
        f"{name}-public-{zone2}-route-table-association",
        subnet_id=public_subnet_zone2.id,
        route_table_id=public_route_table_zone2.id,
        opts=pulumi.ResourceOptions(depends_on=[public_subnet_zone2, public_route_table_zone2])
    )

    # Create a Route Table for the public subnet
    private_route_table_zone2 = ec2.RouteTable(
        f"{name}-private-{zone2}-route-table",
        vpc_id=vpc.id,
        tags={
            "Name": f"{name}-private-{zone2}-route-table",
        },
        opts=pulumi.ResourceOptions(depends_on=[vpc])
    )

    # Associate the public subnet with the Route Table
    private_route_table_association_zone2 = ec2.RouteTableAssociation(
        f"{name}-private-{zone2}-route-table-association",
        subnet_id=private_subnet_zone2.id,
        route_table_id=private_route_table_zone2.id,
        opts=pulumi.ResourceOptions(depends_on=[private_subnet_zone2, private_route_table_zone2])
    )


    # Create Security Groups
    app_sg = ec2.SecurityGroup(
        f"{name}-app-sg",
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
            "Name": f"{name}-app-sg",
        },
        opts=pulumi.ResourceOptions(depends_on=[vpc])
    )

    # Allocate an Elastic IP for the NAT Gateway
    eip = aws.ec2.Eip(f"{name}-eip", vpc=True)

    # Assuming you have a public subnet created and its ID is stored in `public_subnet_id`
    # Replace `public_subnet_id` with the actual variable or method that retrieves your public subnet ID
    nat_gateway = aws.ec2.NatGateway(
        f"{name}-nat-gateway",
        subnet_id=public_subnet_zone1.id,  # Use the ID of the public subnet
        allocation_id=eip.id,
        tags={
            "Name": f"{name}-nat-gateway",
        },
        opts=pulumi.ResourceOptions(depends_on=[vpc, eip])  # Ensure NAT Gateway depends on VPC and EIP
    )

    # Create a route in the Route Table that directs internet-bound traffic to the Internet Gateway
    private_internet_route_zone2 = ec2.Route(
        f"{name}-private-{zone2}-internet-route",
        destination_cidr_block="0.0.0.0/0",
        gateway_id=nat_gateway.id,
        route_table_id=private_route_table_zone2.id,
        opts=pulumi.ResourceOptions(depends_on=[igw, private_route_table_zone2, nat_gateway])
    )

    # Create a route in the Route Table that directs internet-bound traffic to the Internet Gateway
    private_internet_route_zone1 = ec2.Route(
        f"{name}-private-{zone1}-internet-route",
        destination_cidr_block="0.0.0.0/0",
        gateway_id=nat_gateway.id,
        route_table_id=private_route_table_zone1.id,
        opts=pulumi.ResourceOptions(depends_on=[igw, private_route_table_zone1, nat_gateway])
    )

    resources = {
        "vpc": vpc,
        "app_sg": app_sg,
        "igw": igw,
        "eip": eip,
        "nat_gateway": nat_gateway,
        "public_subnet_zone1": public_subnet_zone1,
        "private_subnet_zone1": private_subnet_zone1,
        "public_subnet_zone2": public_subnet_zone2,
        "private_subnet_zone2": private_subnet_zone2,
    }

    return resources