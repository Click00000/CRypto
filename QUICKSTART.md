# 🚀 Hızlı Başlangıç - Exchange Flow Intelligence

## 5 Dakikada Canlıya Alma

### Adım 1: GitHub'a Push

```bash
cd exchange-flow-intelligence
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Adım 2: Render - Backend Setup (5 dk)

1. **PostgreSQL Oluştur**:
   - Render Dashboard → New → PostgreSQL
   - Name: `efi-db`
   - Connection string'i kopyala

2. **Redis Oluştur**:
   - Render Dashboard → New → Redis  
   - Name: `efi-redis`
   - Internal URL'i kopyala

3. **Backend Deploy**:
   - Render Dashboard → New → Web Service
   - Connect GitHub repo
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   
   **Environment Variables**:
   ```
   DATABASE_URL=<postgres-connection-string>
   REDIS_URL=<redis-internal-url>
   JWT_SECRET=<generate-random-32-chars>
   APP_BASE_URL=https://your-app.vercel.app (sonra güncelle)
   API_BASE_URL=https://efi-api.onrender.com
   RESEND_API_KEY=<your-resend-key>
   EMAIL_FROM=noreply@yourdomain.com
   EVM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
   BTC_MODE=EXPLORER
   BTC_EXPLORER_BASE_URL=https://blockstream.info/api
   ADMIN_EMAIL=admin@yourdomain.com
   CORS_ORIGINS=https://your-app.vercel.app (sonra güncelle)
   ```

4. **Worker Deploy**:
   - Render Dashboard → New → Background Worker
   - **Root Directory**: `worker`
   - **Build Command**: `cd ../backend && pip install -r requirements.txt && cd ../worker && pip install -r requirements.txt`
   - **Start Command**: `celery -A app.celery_app worker --loglevel=info & celery -A app.celery_app beat --loglevel=info`
   - Aynı environment variables'ları ekle

### Adım 3: Vercel - Frontend Setup (2 dk)

1. Vercel Dashboard → Add New → Project
2. GitHub repo'yu import et
3. **Root Directory**: `frontend`
4. **Environment Variable**:
   ```
   NEXT_PUBLIC_API_URL=https://efi-api.onrender.com
   ```
5. Deploy et
6. Frontend URL'i kopyala

### Adım 4: Backend'i Güncelle (1 dk)

Render Dashboard → Backend Service → Environment Variables:
- `APP_BASE_URL` → Vercel frontend URL
- `CORS_ORIGINS` → Vercel frontend URL

### Adım 5: Database Seed (1 dk)

Render Dashboard → Backend Service → Shell:
```bash
cd backend
python scripts/seed.py
```

### ✅ Test

1. Frontend URL'e git
2. Admin email ile login ol
3. Admin panel'e git
4. Exchange ekle
5. Address ekle
6. Worker'ın sync yaptığını kontrol et

## 🎉 Tamamlandı!

Artık sisteminiz canlıda çalışıyor. Detaylı bilgi için `DEPLOYMENT.md` dosyasına bakın.
