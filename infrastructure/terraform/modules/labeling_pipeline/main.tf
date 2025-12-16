data "aws_lambda_function" "labeler" {
  function_name = var.lambda_function_name
}

resource "aws_cloudwatch_event_rule" "hourly_backfill" {
  count               = var.enable_hourly_backfill ? 1 : 0
  name                = "rubiks-labeler-hourly-backfill"
  description         = "Hourly backfill to label any unlabeled Rubik's cube face images"
  schedule_expression = "rate(${var.backfill_rate_hours} hour)"
}

resource "aws_cloudwatch_event_target" "invoke_lambda" {
  count = var.enable_hourly_backfill ? 1 : 0
  rule  = aws_cloudwatch_event_rule.hourly_backfill[0].name
  arn   = data.aws_lambda_function.labeler.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  count         = var.enable_hourly_backfill ? 1 : 0
  statement_id  = "AllowExecutionFromEventBridgeBackfill"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.hourly_backfill[0].arn
}