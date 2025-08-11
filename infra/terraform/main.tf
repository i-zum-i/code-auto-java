# Terraform main config placeholder
terraform {
  required_version = ">= 1.6.0"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.50" } }
}

provider "aws" {
  region = var.region
}

locals { name = var.system_name }

# S3 (artifacts/logs)
module "s3" {
  source = "./s3"
}

# DynamoDB (jobs)
module "ddb" {
  source = "./dynamodb"
}

# SQS (jobs queue)
module "sqs" {
  source = "./sqs"
}

# ECR for worker image
module "ecr" {
  source = "./ecr"
}

# ECS Cluster & Fargate Service (worker)
module "ecs" {
  source = "./ecs_cluster"
  queue_url          = module.sqs.queue_url
  jobs_table         = module.ddb.table
  artifacts_bucket   = module.s3.bucket
  ecr_repo_url       = module.ecr.repo_url
}

# API (Lambda + API Gateway HTTP API)
module "api" {
  source = "./lambda_api"
  queue_url  = module.sqs.queue_url
  jobs_table = module.ddb.table
}
