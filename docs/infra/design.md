# インフラ基本設計書

## モジュール構成
- `terraform/main.tf` は各リソースをモジュールとして呼び出す。
- 主要モジュール: `s3`, `dynamodb`, `sqs`, `ecr`, `ecs_cluster`, `lambda_api`。
- 各モジュールはタグ付けと命名規則`<system_name>-<component>`を持つ。

## ネットワーク
- VPC内にパブリックサブネット(外部公開用)とプライベートサブネット(内部処理用)を配置。
- ECS FargateとLambdaはプライベートサブネットに配置し、NAT Gateway経由でインターネットアクセスを行う。
- GitHubやAnthropic APIへの通信はNAT Gatewayを通す。

## CI/CD
- Terraformの状態管理はTerraform CloudまたはS3バックエンドを使用する想定。
- WorkerのコンテナイメージはCIパイプラインでビルドしECRへプッシュする。

## ログ・監視
- すべてのサービスはCloudWatch Logsへ出力。
- 重要イベントにはCloudWatch Alarmsを設定し、必要に応じてSNSで通知する。
