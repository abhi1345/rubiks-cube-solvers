variable "aws_region" { type = string }
variable "bucket_name" { type = string }
variable "lambda_function_name" { type = string }

variable "enable_hourly_backfill" {
  type    = bool
  default = true
}

variable "backfill_rate_hours" {
  type    = number
  default = 1
}