variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1"
}

variable "system_name" {
  description = "System name prefix for resources"
  type        = string
  default     = "code-auto"
}

variable "vpc_id" {
  description = "VPC ID for ECS and other resources"
  type        = string
  default     = ""
}

variable "subnet_ids" {
  description = "Subnet IDs for ECS tasks"
  type        = list(string)
  default     = []
}

variable "claude_api_key" {
  description = "Claude API key (will be stored in Secrets Manager)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "github_app_id" {
  description = "GitHub App ID"
  type        = string
  default     = ""
}

variable "github_app_private_key" {
  description = "GitHub App Private Key (PEM format)"
  type        = string
  sensitive   = true
  default     = ""
}