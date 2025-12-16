terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "labeling_pipeline" {
  source = "../../modules/labeling_pipeline"

  aws_region           = var.aws_region
  bucket_name          = var.bucket_name
  labeling_lambda_function_name = var.labeling_lambda_function_name

  enable_hourly_backfill = true
  backfill_rate_hours    = 1
}