# インフラ要件定義書

## 基本方針
- すべてAWSマネージドサービスで構成し、インフラはコード化(Terraform)する。
- コンポーネント間はプライベートサブネット内で通信し、必要な外部アクセスのみNAT Gatewayから行う。

## 必須リソース
- **API Gateway + Lambda**: フロントからのHTTPリクエストを受け付ける。
- **SQS**: ジョブキューとして利用し、FIFOとする。
- **DynamoDB**: ジョブ状態の永続化。
- **ECS Fargate**: Workerコンテナを実行。gVisor等で隔離。
- **ECR**: Workerコンテナイメージの保存。
- **S3**: 生成パッチ・ログ等の成果物格納。
- **Secrets Manager**: Claude APIキーやGitHub App秘密鍵を管理。
- **VPC/サブネット**: プライベートサブネット構成、必要に応じてVPC Endpointを配置。

## セキュリティ
- IAMロールは最小権限付与。
- すべての通信はTLS1.2以上を使用。
- CloudWatch Logsにより監視とアラートを実施。
