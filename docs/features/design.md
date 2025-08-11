# 機能基本設計書

## コンポーネント
- **API(Lambda)**: HTTPリクエストを受け取り、ジョブを生成してDynamoDBとSQSへ登録する。
- **Worker(ECS Fargate)**: SQSからジョブを取得し、コード生成・CI・PR作成を実施する。
- **DynamoDB**: ジョブの状態およびメタデータを保持する。
- **SQS**: ジョブのキューイングと再実行制御を行う。
- **S3**: パッチやログなど成果物を保存する。

## シーケンス概要
1. APIがジョブを受理し`jobId`を返却。
2. Workerがジョブを取得し、Secrets ManagerからClaude APIキーとGitHub Appの情報を取得。
3. `git_ops.with_checkout`で対象リポジトリをcloneし、`context_extract.build_min_context`で対象ファイルを抽出。
4. `claude_client.plan_and_apply`で実装プランとパッチを生成。
5. `ci_runner.run_ci`でテストを実行し、`git_ops.push_branch_and_open_pr`で新規ブランチとDraft PRを作成。
6. DynamoDBの状態を`pr-open`へ更新し、必要ならコールバック通知。

## エラー処理
- 例外発生時はジョブ状態を`failed`に設定し、エラーメッセージを記録する。
- SQSメッセージは処理後に削除し、再実行が必要な場合はジョブの再投入を行う。
