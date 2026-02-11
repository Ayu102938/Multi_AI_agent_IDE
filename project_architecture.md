multi AI agent IDE project

Monaco Editor + CrewAI + Tree-sitter

スペシャリストのアーキテクチャーは

The Architect (Leader): ユーザーの要望（例：「ログイン機能追加して」）を、「DB設計」「API実装」「UI実装」に分解し、各エージェントに投げる。

The Coder: 言語ごとに特化（Python担当、React担当など）。

The Critic (Reviewer): 生成されたコードに対して、セキュリティ脆弱性やベストプラクティス違反がないかだけを監視する。

The Tester: コードが生成された瞬間に、そのコードをテストする単体テストを書き、バックグラウンドで実行まで行う。

The Librarian: ドキュメントの更新や、READMEの追記を専門に行う。