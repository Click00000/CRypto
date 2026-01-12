# 🤖 Otomatik Deployment Rehberi

Bu rehber Render ve Vercel'e otomatik deployment için adımları içerir.

## 🚀 Hızlı Başlangıç

### 1. GitHub'a Push

```bash
# Script ile otomatik
chmod +x deploy.sh
./deploy.sh

# Veya manuel
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Render Deployment (2 Yöntem)

#### Yöntem A: Blueprint (Önerilen - Otomatik)

1. Render Dashboard → **New** → **Blueprint**
2. GitHub repo'nuzu seçin
3. `render.yaml` dosyası otomatik algılanır
4. **Apply** butonuna tıklayın
5. Eksik environment variables'ları doldurun:
   - `RESEND_API_KEY`
   - `EVM_RPC_URL`
   - `ADMIN_EMAIL`
   - `API_BASE_URL` (deploy sonrası backend URL)
   - `APP_BASE_URL` ve `CORS_ORIGINS` (Vercel URL sonrası)

#### Yöntem B: Manuel (Adım Adım)

**PostgreSQL:**
1. New → PostgreSQL
2. Name: `efi-db`
3. Connection string'i kopyala

**Redis:**
1. New → Redis
2. Name: `efi-redis`
3. Internal URL'i kopyala

**Backend API:**
1. New → Web Service
2. Connect GitHub repo
3. **Root Directory**: `backend`
4. **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
5. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Environment Variables ekle (aşağıdaki listeye bak)

**Worker:**
1. New → Background Worker
2. Connect GitHub repo
3. **Root Directory**: `worker`
4. **Build Command**: `cd ../backend && pip install -r requirements.txt && cd ../worker && pip install -r requirements.txt`
5. **Start Command**: `celery -A app.celery_app worker --loglevel=info & celery -A app.celery_app beat --loglevel=info`
6. Aynı environment variables'ları ekle

### 3. Vercel Deployment

#### Yöntem A: GitHub Integration (Önerilen)

1. Vercel Dashboard → **Add New** → **Project**
2. GitHub repo'nuzu import et
3. **Root Directory**: `frontend` (otomatik algılanabilir)
4. **Framework Preset**: Next.js (otomatik)
5. **Environment Variable** ekle:
   ```
   NEXT_PUBLIC_API_URL=https://efi-api.onrender.com
   ```
6. **Deploy** butonuna tıkla

#### Yöntem B: Vercel CLI

```bash
cd frontend
npm install -g vercel
vercel
# Soruları yanıtla
# Environment variable ekle: NEXT_PUBLIC_API_URL
```

### 4. Environment Variables Güncelle

**Render Backend'de:**
- `APP_BASE_URL` → Vercel frontend URL
- `API_BASE_URL` → Render backend URL (https://efi-api.onrender.com)
- `CORS_ORIGINS` → Vercel frontend URL

### 5. Database Seed

Render Dashboard → Backend Service → **Shell**:
```bash
cd backend
python scripts/seed.py
```

## 📋 Environment Variables Listesi

### Render Backend & Worker

```bash
# Database & Redis (otomatik - Blueprint kullanıyorsanız)
DATABASE_URL=<postgres-connection-string>
REDIS_URL=<redis-internal-url>

# JWT
JWT_SECRET=<32+ karakter random string>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168

# URLs (deploy sonrası güncelle)
APP_BASE_URL=https://your-frontend.vercel.app
API_BASE_URL=https://efi-api.onrender.com
CORS_ORIGINS=https://your-frontend.vercel.app

# Email
RESEND_API_KEY=<resend-api-key>
EMAIL_FROM=noreply@yourdomain.com

# Blockchain
EVM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
BTC_MODE=EXPLORER
BTC_EXPLORER_BASE_URL=https://blockstream.info/api
BTC_EXPLORER_API_KEY=  # Opsiyonel

# Admin
ADMIN_EMAIL=admin@yourdomain.com
```

### Vercel Frontend

```bash
NEXT_PUBLIC_API_URL=https://efi-api.onrender.com
```

## ✅ Deployment Sonrası Kontrol

1. **Backend Health Check**:
   ```
   https://efi-api.onrender.com/health
   ```
   Response: `{"status":"ok"}`

2. **Frontend**:
   ```
   https://your-frontend.vercel.app
   ```
   Login sayfası görünmeli

3. **Database Seed**:
   - Render Shell'den seed çalıştır
   - Admin user oluşturuldu mu kontrol et

4. **Magic Link Test**:
   - Frontend'de admin email ile login dene
   - Email geliyor mu kontrol et

5. **Admin Panel**:
   - Login sonrası admin panel erişilebilir mi?
   - Exchange ekleme çalışıyor mu?

## 🔧 Troubleshooting

### Backend başlamıyor
- Logları kontrol et: Render Dashboard → Logs
- Environment variables eksik olabilir
- Database connection string yanlış olabilir

### Worker çalışmıyor
- Redis connection kontrol et
- PYTHONPATH ayarlı mı?
- Worker logs: Render Dashboard → Logs

### Frontend build hatası
- `NEXT_PUBLIC_API_URL` set edilmiş mi?
- Root directory `frontend` mi?
- Build logs kontrol et

### CORS hatası
- `CORS_ORIGINS` frontend URL'i içeriyor mu?
- Backend'de `APP_BASE_URL` doğru mu?

## 🎉 Başarılı!

Deployment tamamlandı! Artık sisteminiz canlıda çalışıyor.

**İlk Kullanım:**
1. Admin email ile login ol
2. Admin panel → Exchange ekle
3. Admin panel → Address ekle
4. Worker otomatik sync başlayacak
5. Dashboard'da alerts ve flows görüntüle
