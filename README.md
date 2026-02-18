# Multi-Agent IDE

## プロジェクト概要
**Multi-Agent IDE** は、複数の専門的なAIエージェントが協調してソフトウェア開発を行う、次世代の統合開発環境（IDE）です。
ユーザーは自然言語で要件を伝えるだけで、アーキテクト、コーダー、テスターなどの役割を持つAIエージェントが連携し、設計から実装、テストまでを自律的に実行します。

## アーキテクチャ

本プロジェクトは、モダンなWeb技術と強力なAIフレームワークを組み合わせた構成になっています。
詳細は [`project_architecture.md`](./project_architecture.md) を参照してください。

### バックエンド (Backend)
- **Framework**: FastAPI (Python 3.13+)
- **AI Orchestration**: CrewAI (Sequential Process)
- **LLM**: ZhiPu AI GLM-4.5-Flash（プライマリ）/ Google Gemini（フォールバック）
- **パッケージ管理**: uv
- **主要コンポーネント**:
    - `main.py`: APIサーバーのエントリーポイント。REST APIを提供。
    - `agents.py`: CrewAIを使用したエージェント（Architect, Coder, Critic, Tester, Librarian）の定義。
    - `safe_tools.py`: サンドボックス化されたファイル操作ツール（SafeFileWriterTool, SafeFileReaderTool）。
    - `logger.py`: エージェントのリアルタイムログ収集・配信。
    - `workspace/`: エージェントが生成したファイルを保存するサンドボックスディレクトリ。

### フロントエンド (Frontend)
- **Framework**: React 19 + Vite 7
- **Editor**: Monaco Editor (VS Codeのコアエディタ)
- **HTTP Client**: Axios
- **主要機能**:
    - チャットインターフェース: AIへの指示出し。
    - ファイルエクスプローラー: ワークスペース内のファイル一覧・閲覧。
    - リアルタイム Activity Log: エージェントの思考プロセスを可視化。
    - コードエディタ: 生成されたコードの閲覧・編集。
    - コード実行: Python コードの実行と結果表示。

### エージェント構成
1. **Architect**: 要件定義、技術選定、ファイル構成の設計。
2. **Coder**: 設計に基づいたコードの実装、ワークスペースへの書き込み。
3. **Critic**: コードのセキュリティ・品質レビュー。
4. **Tester**: テストケースの作成と実行、品質保証。
5. **Librarian**: ドキュメント（README等）の整備と更新。

### セキュリティ
- **サンドボックスファイルI/O**: `SafeFileWriterTool` / `SafeFileReaderTool` により、エージェントのファイル操作は `workspace/` 内に制限。パストラバーサル攻撃（`../../main.py` 等）を検出・ブロック。
- **APIキー管理**: `.env` ファイルで管理、`.gitignore` により git 履歴からの漏洩を防止。

## 現在の機能

### ✅ Phase 1: 基本機能（完了）
- [x] 対話型コード生成（自然言語 → コード）
- [x] リアルタイムActivity Log（エージェント思考過程の可視化）
- [x] Pythonコード実行と結果表示
- [x] Monaco Editor によるコード編集

### ✅ Phase 2: ファイルI/O & ワークフロー改善（完了）
- [x] エージェント専用ワークスペースの構築
- [x] SafeFileWriterTool / SafeFileReaderTool（セキュアなファイルI/O）
- [x] フロントエンド ファイルエクスプローラー
- [x] 複数ファイル（モジュール import 含む）の実行サポート
- [x] CORS設定・ダークモードUI統一
- [x] LLM切替: ZhiPu AI GLM-4.5-Flash（プライマリ）
- [x] エージェントログ改善（per-task コールバック、出力全文表示）

### 🔜 Phase 3: 高度な機能と安全性（計画中）
- [ ] サンドボックス実行環境（Docker/WebAssembly）
- [ ] プロジェクト管理（複数セッション保存・切替）
- [ ] Git連携（エージェントによるコミット・PR作成）
- [ ] LSP統合（高度な補完・エラーチェック）
- [ ] WebSocket通信（ポーリング → リアルタイム）

## セットアップと実行

### 必要要件
- Python 3.13+
- Node.js 18+
- uv（Pythonパッケージマネージャー）
- ZhiPu AI API Key または Google API Key

### ローカル開発環境での起動

1. **バックエンド**
```bash
cd backend
cp .env.example .env
# .env ファイルに API キーを設定
uv sync
uv run uvicorn main:app --reload
```

2. **フロントエンド**
```bash
cd frontend
npm install
npm run dev
```

3. **アクセス**
- フロントエンド: `http://localhost:5173`
- バックエンドAPI: `http://localhost:8000`
- API ドキュメント: `http://localhost:8000/docs`

## 環境変数

| 変数名 | 必須 | 説明 |
|--------|------|------|
| `ZHIPUAI_API_KEY` | △ | ZhiPu AI API キー（推奨プライマリ） |
| `GOOGLE_API_KEY` | △ | Google Gemini API キー（フォールバック） |
| `OPENAI_API_KEY` | △ | OpenAI API キー（CrewAI デフォルト） |

> **注**: 上記のうち少なくとも1つが必要です。すべて未設定の場合はデモモードで動作します。
