# Elon Musk AI - 無料デプロイガイド (カード登録なし)

Renderでカード登録が必要な場合、**Koyeb (バックエンド)** と **Vercel (フロントエンド)** の組み合わせがおすすめです。どちらも完全無料で、クレジットカード登録なしで開始できます。

## 手順概要
1. **Koyeb**: バックエンド (Python/FastAPI) をデプロイ
2. **Vercel**: フロントエンド (Next.js) をデプロイ

---

## 1. バックエンド (Koyeb)

[Koyeb](https://www.koyeb.com/) はDockerコンテナを無料で動かせるPaaSです。

1. **[Koyebにサインアップ](https://app.koyeb.com/auth/signup)** (GitHubアカウントでログイン)
2. **Create App** をクリック
3. **GitHub** を選択し、リポジトリ `salmonBasilCheese/elon-musk-ai` を選択
4. **Builder** 設定:
   - **Use Dockerfile** を選択
   - **Dockerfile location**: `backend/Dockerfile` (重要！)
   - **Privileged**: OFF (そのままでOK)
5. **Environment Variables** (Add Variable):
   - Key: `OPENAI_API_KEY`
   - Value: (あなたのAPIキー)
6. **Deploy** をクリック

デプロイ完了後、`https://<app-name>.koyeb.app` のようなURLが発行されます。これが **バックエンドURL** です。

---

## 2. フロントエンド (Vercel)

Next.jsの開発元であるVercelを使います。

1. **[Vercelにサインアップ](https://vercel.com/signup)** (GitHub連携)
2. **Add New...** → **Project** をクリック
3. リポジトリ `elon-musk-ai` の **Import** をクリック
4. **Configure Project** 画面で:
   - **Framework Preset**: Next.js (自動検出されるはず)
   - **Root Directory**: `Edit` を押して `frontend` を選択 (重要！)
5. **Environment Variables**:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: (Koyebで取得したバックエンドURL) ※末尾の `/` は不要
6. **Deploy** をクリック

---

## 完了

Vercelから発行されたURLにアクセスすれば、アプリが動作します！
