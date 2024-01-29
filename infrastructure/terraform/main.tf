terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

// Region speficied in AWS provider
data "aws_region" "current" {}
