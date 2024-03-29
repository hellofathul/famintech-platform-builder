import pulumi
import pulumi_aws as aws
from aws_platform import Platform  # Import the Platform class from platform.py

# Configs
config = pulumi.Config()
stack_key = pulumi.get_project()
stack_env = pulumi.get_stack()

# Defaults
stack_full_name = f"{stack_key}-{stack_env}"

famintech_platform_builder = Platform(stack_full_name, {
    "platform": {

    }
})
