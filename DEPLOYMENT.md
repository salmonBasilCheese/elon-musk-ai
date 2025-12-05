# Elon Musk AI - Deployment Guide

## デプロイ手順

### Step 1: GitHubリポジトリ

リポジトリの作成とコードのプッシュは完了しています。
URL: **https://github.com/salmonBasilCheese/elon-musk-ai**

### Step 2: Renderでデプロイ

以下のボタンから簡単にデプロイできます（Renderアカウントが必要です）：

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/salmonBasilCheese/elon-musk-ai)

または手動で設定する場合：

1. [Render Dashboard](https://dashboard.render.com/) にアクセス
2. **New** → **Blueprint** をクリック
3. リポジトリ `salmonBasilCheese/elon-musk-ai` を接続
4. **Service Name** はそのままでOK
5. **Environment Variables** の設定を求められたら入力：
   - `OPENAI_API_KEY`: あなたのOpenAI APIキー
6. **Apply** をクリック

### 完了！

デプロイが完了すると、RenderからURLが発行されます。

---

## 重要な注意事項

- **OpenAI APIキー**: Blueprint設定時に必ず入力してください
- **無料プラン**: Renderの無料プランは15分アイドルでスリープします（初回アクセスが遅くなります）
