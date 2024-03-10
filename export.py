import pulumi

def export_resources(name, zone1, zone2, resources):
    pulumi.export("vpc_id", resources["vpc"].id)
    pulumi.export("app_sg_id", resources["app_sg"].id)
    pulumi.export("igw_id", resources["igw"].id)
    pulumi.export("eip_id", resources["eip"].id)
    pulumi.export("nat_gateway_id", resources["nat_gateway"].id)
    pulumi.export(f"{name}-public-{zone1}", resources["public_subnet_zone1"].id)
    pulumi.export(f"{name}-private-{zone1}", resources["private_subnet_zone1"].id)
    pulumi.export(f"{name}-public-{zone2}", resources["public_subnet_zone2"].id)
    pulumi.export(f"{name}-private-{zone2}", resources["private_subnet_zone2"].id)