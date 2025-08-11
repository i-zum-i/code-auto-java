# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a code automation system designed to work with Java projects, consisting of:
- **API service**: REST API for handling code automation requests (OpenAPI specification)
- **Worker service**: Python-based worker that processes automation tasks
- **Infrastructure**: Terraform configuration for AWS deployment
- **CI/CD**: GitHub Actions workflow for pull request validation

## Architecture

The system follows a microservices architecture:

```
services/
├── api/           # REST API service (OpenAPI spec)
└── worker/        # Python worker service
    ├── app/
    │   ├── worker.py      # Main worker implementation
    │   ├── tools/
    │   │   └── git_ops.py # Git operations utilities
    │   └── prompts/
    │       └── implement.md # Prompt templates
```

## Infrastructure

- **Cloud Provider**: AWS (configured via Terraform)
- **Infrastructure as Code**: Terraform configurations in `infra/terraform/`
- **Deployment**: Architecture diagrams available in `diagrams/` directory

## Development Commands

Note: This project appears to be in early setup phase. Most implementation files are currently placeholders. Common development commands will need to be added as the actual implementation progresses.

## Key Files and Directories

- `services/api/openapi.yaml` - API specification
- `services/worker/app/worker.py` - Core worker logic
- `services/worker/app/tools/git_ops.py` - Git operations
- `infra/terraform/main.tf` - AWS infrastructure configuration
- `ci/github/workflows/pr-ci.yml` - CI/CD pipeline
- `diagrams/` - System architecture diagrams

## CI/CD

GitHub Actions workflow configured in `ci/github/workflows/pr-ci.yml` for pull request validation.

## Notes

This codebase appears to be in the initial setup phase with placeholder files. As implementation progresses, this CLAUDE.md should be updated with:
- Specific build/test/lint commands
- Deployment procedures
- Development setup instructions
- Testing strategies