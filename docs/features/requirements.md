# 機能要件定義書

## API機能
- `/jobs` へ指示文とリポジトリ参照(`repoRef`)を受け取りジョブを生成する。
- `/jobs/{jobId}` でジョブ状態・PR URLを取得できる。
- `/jobs/{jobId}:cancel` で実行中ジョブのキャンセルを要求できる。

## ジョブ処理
- 受け付けたジョブはSQSキューに投入する。
- ワーカーはキューからジョブを取得し、対象リポジトリをshallow clone + sparse checkoutする。
- `context_extract` により最小限のファイルを抽出し、Claude Codeへ渡す。
- `git_ops` がブランチ作成とPull Request作成を行う。
- `ci_runner` によりMavenまたはGradleのビルド・テスト・Lintを実行する。
- 処理結果はDynamoDBへ更新し、必要に応じてコールバックURLへ通知する。

## 監査・ログ
- 各ジョブの入力プロンプト、生成パッチ、実行ログをS3へ保存する。
- 機微情報は自動的にマスキングする。
