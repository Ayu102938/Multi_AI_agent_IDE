# Multi-Agent IDE

## プロジェクト概要
**Multi-Agent IDE** は、複数の専門的なAIエージェントが協調してソフトウェア開発を行う、次世代の統合開発環境（IDE）です。
ユーザーは自然言語で要件を伝えるだけで、アーキテクト、コーダー、テスターなどの役割を持つAIエージェントが連携し、設計から実装、テストまでを自律的に実行します。

## アーキテクチャ

本プロジェクトは、モダンなWeb技術と強力なAIフレームワークを組み合わせた構成になっています。

### バックエンド (Backend)
- **Framework**: FastAPI (Python)
- **AI Orchestration**: CrewAI
- **LLM**: Google Gemini (via LiteLLM `gemini/gemini-flash-latest`)
- **主要コンポーネント**:
    - `main.py`: APIサーバーのエントリーポイント。WebSocket/REST APIを提供。
    - `agents.py`: CrewAIを使用したエージェント（Architect, Coder, Tester, Librarian）の定義。
    - `workspace/`: エージェントが生成したファイルを保存するサンドボックスディレクトリ。
    - **Tools**: `FileReadTool`, `FileWriterTool` (crewai_tools) を使用してファイル操作を実現。

### フロントエンド (Frontend)
- **Framework**: React + Vite
- **Editor**: Monaco Editor (VS Codeのコアエディタ)
- **UI**: シンプルかつ機能的なシングルページアプリケーション (SPA)。
- **主要機能**:
    - チャットインターフェース: AIへの指示出し。
    - リアルタイムログ: エージェントの思考プロセス（Thinking/Action）を可視化。
    - コードエディタ: 生成されたコードの閲覧・編集・実行。

### エージェント構成
1. **Architect**: 要件定義、技術選定、ファイル構成の設計。
2. **Coder**: 設計に基づいたコードの実装、ファイルへの書き込み。
3. **Tester**: コードのレビュー、テストケースの作成と実行（ファイル保存）。
4. **Librarian**: ドキュメント（README等）の整備と更新。

## 現在の機能 (Phase 1 Completed)
- [x] **対話型コード生成**: 自然言語による指示からコードを生成。
- [x] **リアルタイム可視化**: エージェントの推論過程をログとして表示。
- [x] **コード実行**: 生成されたPythonコードをバックエンドで実行し、結果を表示（`exec`使用）。
- [x] **Gemini連携**: 高速かつ安価なGemini Flashモデルでの安定動作。

## 今後の改善計画 (Roadmap)

### Phase 2: Agent I/O & Workflow Improvements (現在進行中)
エージェントがチャットだけでなく、実際のファイルシステムを操作できる「ファイルベース」のワークフローへ移行します。
- [x] **Workspace設定**: エージェント専用の作業ディレクトリの整備。
- [x] **File Tools導入**: エージェントによるファイルの読み書き能力の付与。
- [x] **Workspace API**: フロントエンドからファイルを一覧・取得するAPIの実装。
- [ ] **Frontend File Explorer**: 生成されたファイルをブラウズ・開くためのUI実装。
- [ ] **Multi-file Execution**: 複数ファイル（モジュールimport含む）の実行サポート。

### Phase 3: Advanced Features & Safety
- **サンドボックス実行環境**: Docker等を使用した安全なコード実行（現在の`exec`からの脱却）。
- **プロジェクト管理**: 複数のプロジェクト/セッションの保存と切り替え。
- **Git連携**: エージェントによるコミットやプルリクエスト作成。
- **LSP統合**: Monaco Editorでの高度な補完やエラーチェック。

## セットアップと実行

### 必要要件
- Docker (推奨) または Python 3.10+ & Node.js 18+
- Google API Key (Gemini用)

### ローカル開発環境での起動

1. **バックエンド**
```bash
cd backend
# .envファイルを作成し、GOOGLE_API_KEYを設定
uv run uvicorn main:app --reload
```

2. **フロントエンド**
```bash
cd frontend
npm install
npm run dev
```

3. **アクセス**
ブラウザで `http://localhost:5173` を開いてください。
