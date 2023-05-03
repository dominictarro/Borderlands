/*
Network resources for the Borderlands infrastructure.


The ECS cluster the Prefect Agent runs on requires a VPC and subnet to run it in. The
subnet must have inbound and outbound routes to the internet.
*/

/*
Network variables.
*/
variable "vpc_availability_zone" {
    type = string
    description = "Availability zone for the VPC."
    default = "us-east-1a"
}

variable "vpc_cidr_block" {
  type = string
  description = "CIDR for the VPC."
  default = "10.0.0.0/16"
}

variable "vpc_public_subnet_cidr_block" {
  type = string
  description = "CIDR for the public subnet."
  default = "10.0.1.0/24"
}

variable "vpc_private_subnet_cidr_block" {
  type = string
  description = "CIDR for the private subnet."
  default = "10.0.2.0/24"
}

/*
Network for Prefect to operate within.

Contains 1 public subnet and 1 private subnet.

To expand the number of subnets, note the changes from this guide

https://spacelift.io/blog/terraform-aws-vpc


*/
resource "aws_vpc" "borderlands_vpc" {
    cidr_block = var.vpc_cidr_block
}

resource "aws_subnet" "borderlands_public_subnet" {
    vpc_id = aws_vpc.borderlands_vpc.id
    cidr_block = var.vpc_public_subnet_cidr_block
    availability_zone = var.vpc_availability_zone
}

resource "aws_subnet" "borderlands_private_subnet" {
    vpc_id = aws_vpc.borderlands_vpc.id
    cidr_block = var.vpc_private_subnet_cidr_block
    availability_zone = var.vpc_availability_zone
}

resource "aws_internet_gateway" "borderlands_igw" {
    vpc_id = aws_vpc.borderlands_vpc.id
}

resource "aws_route_table" "borderlands_public_rt" {
 vpc_id = aws_vpc.borderlands_vpc.id
 
 route {
   cidr_block = "0.0.0.0/0"
   gateway_id = aws_internet_gateway.borderlands_igw.id
 }
 
}

resource "aws_route_table_association" "borderlands_public_subnet_rt_association" {
    subnet_id = aws_subnet.borderlands_public_subnet.id
    route_table_id = aws_route_table.borderlands_public_rt.id
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

/*
Network outputs.
*/

output "borderlands_vpc_id" {
    description = "VPC ID for Borderlands AWS infrastructure."
    value = aws_vpc.borderlands_vpc.id
}
