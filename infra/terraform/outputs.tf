output "api_gateway_url" {
  description = "API Gateway HTTP API URL"
  value       = module.api.api_url
}

output "queue_url" {
  description = "SQS Queue URL"
  value       = module.sqs.queue_url
}

output "jobs_table_name" {
  description = "DynamoDB Jobs Table Name"
  value       = module.ddb.table_name
}

output "artifacts_bucket_name" {
  description = "S3 Artifacts Bucket Name"
  value       = module.s3.bucket_name
}

output "ecr_repository_url" {
  description = "ECR Repository URL"
  value       = module.ecr.repository_url
}

output "worker_cluster_name" {
  description = "ECS Cluster Name"
  value       = module.ecs.cluster_name
}