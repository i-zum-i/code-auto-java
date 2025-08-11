# ツール基本設計書

## git_ops
- `with_checkout(repoRef)`
  - `repoRef`形式: `github:owner/repo#branch:subdir`。
  - shallow clone後、必要に応じてsparse-checkoutを設定。
  - コンテキストとして`repo_dir`等を返すコンテキストマネージャ。
- `push_branch_and_open_pr(ctx, jobId, patch)`
  - 新規ブランチ `auto/{jobId}` を作成し、パッチをコミットしてDraft PRを作成。

## context_extract
- プロジェクトルートから`pom.xml`または`build.gradle(.kts)`を探索し、関連する`src/main` `src/test`ディレクトリを収集。
- `application*.yml` 等の設定ファイルも候補に含める。
- 200KBを超えるファイルは除外。

## ci_runner
- プロジェクトルートに`pom.xml`があれば`mvn -B -ntp verify`を実行。
- `build.gradle`または`build.gradle.kts`があれば`./gradlew test`を実行。
- 結果を標準出力で返す。

## claude_client
- `plan_and_apply`が指示文とファイル一覧を元にClaudeに問い合わせ、実装プランとパッチを生成。
- 応答パッチは`git apply`で適用可能な形式とする。
