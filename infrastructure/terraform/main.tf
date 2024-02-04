terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  profile = "default"
}

// Region speficied in AWS provider
data "aws_region" "current" {}

variable "vpc_id" {
  description = "The VPC ID where resources will be created."
  type        = string
}