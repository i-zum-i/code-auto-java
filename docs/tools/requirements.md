# ツール要件定義書

## git_ops
- GitHub Appインストールトークンを用いてリポジトリをshallow cloneする。
- 必要に応じてsparse-checkoutを設定する。
- 新規ブランチの作成とDraft Pull Requestの作成を行う。

## context_extract
- Java/Gradle/Mavenプロジェクトを対象に、必要最小限のファイルセットを抽出する。
- 指定拡張子とサイズ上限を基にファイルをフィルタリングする。

## ci_runner
- ルートディレクトリからMavenかGradleを自動判別し、ビルド・テスト・Lintを実行する。
- 失敗時は詳細ログを返却する。

## claude_client
- 指示文と抽出したファイルを入力として実装プランとパッチを生成する。
- APIキーはSecrets Managerから取得し、実行後はメモリから消去する。
- 入出力は監査ログ用に保存する。
