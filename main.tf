provider "aws" {
  region = "eu-north-1"
}
resource "aws_iam_policy" "s3_full_access_policy" {
  name        = "s3_full_access_policy"
  description = "Policy for full access to S3"

  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action   = [
          "s3:GetObject",
          
          "s3:GetBucketTagging",
          "s3:PutBucketTagging",
          
          "s3:ListAllMyBuckets",
        ],
        Effect   = "Allow",
        Resource = ["arn:aws:s3:::*"],
      },
    ],
  })
}

module "lambda_function" {
  source           = "terraform-aws-modules/lambda/aws"
  function_name    = "s3_bucket_tagging"
  description      = "My awesome lambda function"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.10"
  source_path      = "./lambda_function.py"
  timeout          = 46 #if we use list_bucket and tagging_all_buckets then 46 sec may be not enought to do it  
  attach_policies  = true
  number_of_policies = 1
  publish          = true
  policies         = [aws_iam_policy.s3_full_access_policy.arn]

  allowed_triggers = {
    Eventbridge = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.s3_bucket_created_rule.arn
    }              
  }

  tags = {
    Name = "my-lambda1"
  }
}
resource "aws_cloudwatch_event_rule" "s3_bucket_created_rule" {
  name        = "s3-bucket-created-rule"
  description = "Fires when a new S3 bucket is created"

  event_pattern = jsonencode({
    "source"      : ["aws.s3"],
    "detail-type" : ["AWS API Call via CloudTrail"],
    "detail"      : {
      "eventSource": ["s3.amazonaws.com"],
      "eventName"  : ["CreateBucket"]
    }
  })
}
resource "aws_cloudwatch_event_target" "s3_bucket_created_target" {
  rule      = aws_cloudwatch_event_rule.s3_bucket_created_rule.name
  
  arn       = module.lambda_function.lambda_function_arn
}


