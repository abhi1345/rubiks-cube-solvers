variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "bucket_name" {
  type = string
}

variable "labeling_lambda_function_name" {
  type = string
}

variable "lambda_role_name" {
  description = "Lambda execution role name"
  type        = string
}