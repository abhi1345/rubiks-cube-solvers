output "backfill_rule_arn" {
  value = try(aws_cloudwatch_event_rule.hourly_backfill[0].arn, null)
}