/*
Network resources for the Borderlands infrastructure.


The ECS cluster the Prefect Agent runs on requires a VPC and subnet to run it in. The
subnet must have inbound and outbound routes to the internet.
*/


resource "aws_vpc_ipam" "borderlands_ipam" {
  operating_regions {
    region_name = data.aws_region.current.name
  }
}

resource "aws_vpc_ipam_pool" "borderlands_ipam_pool" {
  address_family = "ipv4"
  ipam_scope_id  = aws_vpc_ipam.borderlands_ipam.private_default_scope_id
  locale         = data.aws_region.current.name
}

resource "aws_vpc_ipam_pool_cidr" "boderlands_ipam_pool_cidr" {
  ipam_pool_id = aws_vpc_ipam_pool.borderlands_ipam_pool.id
  cidr         = "172.2.0.0/16"
}

resource "aws_vpc" "borderlands_vpc" {
  ipv4_ipam_pool_id   = aws_vpc_ipam_pool.borderlands_ipam_pool.id
  ipv4_netmask_length = 20
  // CIDR must be created before network initialized
  depends_on  = [
    aws_vpc_ipam_pool_cidr.boderlands_ipam_pool_cidr
  ]
}

resource "aws_subnet" "borderlands_subnet" {
  vpc_id            = aws_vpc.borderlands_vpc.id
  # Mask must be size of aws_vpc.borderlands_vpc.ipv4_netmask_length
  cidr_block        = "172.2.0.0/20"
  // CIDR must be created before subnet initialized
  depends_on = [
    aws_vpc_ipam_pool_cidr.boderlands_ipam_pool_cidr
  ]
}

/*
Traffic control
*/

resource "aws_network_acl" "borderlands_acl" {
  vpc_id = aws_vpc.borderlands_vpc.id
}

resource "aws_network_acl_rule" "borderlands_ingress" {
  network_acl_id = aws_network_acl.borderlands_acl.id
  rule_number    = 100
  egress         = false
  protocol       = "-1"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
}

resource "aws_network_acl_rule" "borderlands_egress" {
  network_acl_id = aws_network_acl.borderlands_acl.id
  rule_number    = 100
  egress         = true
  protocol       = "-1"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
}

# Associate the subnet with the ACL
resource "aws_network_acl_association" "borderlands_subnet_acl" {
  subnet_id      = aws_subnet.borderlands_subnet.id
  network_acl_id = aws_network_acl.borderlands_acl.id
}

/*
Network routing
*/

resource "aws_internet_gateway" "borderlands_iag" {
  vpc_id = aws_vpc.borderlands_vpc.id
}

resource "aws_route_table" "borderlands_rt" {
  vpc_id = aws_vpc.borderlands_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.borderlands_iag.id
  }
}

# Associate the subnet with the route table
resource "aws_route_table_association" "borderlands_subnet_rt" {
  subnet_id       = aws_subnet.borderlands_subnet.id
  route_table_id  = aws_route_table.borderlands_rt.id
}


/*
Security resources for the Prefect Agent.
*/

resource "aws_security_group" "prefect_agent" {
  name        = "prefect-agent-sg-${var.name}"
  description = "ECS Prefect Agent"
  vpc_id      = aws_vpc.borderlands_vpc.id
}

resource "aws_security_group_rule" "https_outbound" {
  // S3 Gateway interfaces are implemented at the routing level which means we
  // can avoid the metered billing of a VPC endpoint interface by allowing
  // outbound traffic to the public IP ranges, which will be routed through
  // the Gateway interface:
  // https://docs.aws.amazon.com/AmazonS3/latest/userguide/privatelink-interface-endpoints.html
  description       = "HTTPS outbound"
  type              = "egress"
  security_group_id = aws_security_group.prefect_agent.id
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]

}
