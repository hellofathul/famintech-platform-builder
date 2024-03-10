import pulumi
from pulumi_aws import ec2
import pulumi_aws as aws
from network import create_vpc
from export import export_resources

class Platform:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.platform = {}
        self.zone1 = "ap-southeast-1a"
        self.zone2 = "ap-southeast-1b"

        vpc = create_vpc(self.name, self.zone1, self.zone2)
            
        # Store references to the created network resources
        self.platform.update(vpc)

        # Export the output
        export_resources(self.name, self.zone1, self.zone2, self.platform)




   

           
