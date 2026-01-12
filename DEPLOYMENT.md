# Deployment Guide - Exchange Flow Intelligence

Bu doküman Vercel (Frontend) ve Render (Backend + Worker) deployment adımlarını içerir.

## 📋 Ön Hazırlık

1. **GitHub Repository**: Tüm kodu bir GitHub repository'ye push edin
2. **Resend Account**: Email göndermek için Resend hesabı oluşturun (veya SendGrid/SES)
3. **EVM RPC**: Alchemy, Infura veya başka bir Ethereum RPC provider
4. **Bitcoin RPC/Explorer**: Bitcoin Core RPC veya Blockstream Explorer API

## 🚀 Render Deployment (Backend + Worker)

### 1. PostgreSQL Database Oluştur

1. Render Dashboard → New → PostgreSQL
2. Database adı: `efi-db`
3. Region seçin
4. **Önemli**: Connection string'i kopyalayın (DATABASE_URL olarak kullanılacak)

### 2. Redis Instance Oluştur

1. Render Dashboard → New → Redis
2. Redis adı: `efi-redis`
3. Region seçin (database ile aynı region önerilir)
4. **Önemli**: Internal Redis URL'i kopyalayın

### 3. Backend API Deploy

1. Render Dashboard → New → Web Service
2. **Connect Repository**: GitHub repo'nuzu seçin
3. **Settings**:
   - **Name**: `efi-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables** ekleyin:
   ```
   DATABASE_URL=<PostgreSQL connection string>
   REDIS_URL=<Redis internal URL>
   JWT_SECRET=<32+ karakterlik güvenli random string>
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_HOURS=168
   APP_BASE_URL=https://your-frontend.vercel.app
   API_BASE_URL=https://efi-api.onrender.com
   RESEND_API_KEY=<Resend API key>
   EMAIL_FROM=noreply@yourdomain.com
   EVM_RPC_URL=<Ethereum RPC URL>
   BTC_MODE=EXPLORER
   BTC_EXPLORER_BASE_URL=https://blockstream.info/api
   BTC_EXPLORER_API_KEY=
   ADMIN_EMAIL=admin@yourdomain.com
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```
5. **Advanced** → **Add Disk**: Persistent disk ekleyin (opsiyonel, sadece local file storage için)
6. **Create Web Service**

### 4. Worker Deploy

1. Render Dashboard → New → Background Worker
2. **Connect Repository**: Aynı GitHub repo
3. **Settings**:
   - **Name**: `efi-worker`
   - **Root Directory**: `worker`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     cd ../backend && pip install -r requirements.txt && cd ../worker && pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     celery -A app.celery_app worker --loglevel=info & celery -A app.celery_app beat --loglevel=info
     ```
4. **Environment Variables**: Backend ile aynı environment variables'ları ekleyin
5. **Create Background Worker**

### 5. Seed Database

Deploy sonrası, Render shell'den veya local'den seed çalıştırın:

```bash
# Render shell'den
cd backend
python scripts/seed.py

# Veya local'den (DATABASE_URL'i set edin)
export DATABASE_URL=<your-database-url>
cd backend
python scripts/seed.py
```

## 🌐 Vercel Deployment (Frontend)

### 1. Vercel Project Oluştur

1. Vercel Dashboard → Add New → Project
2. GitHub repo'nuzu import edin
3. **Project Settings**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (otomatik)
   - **Output Directory**: `.next` (otomatik)
   - **Install Command**: `npm install` (otomatik)

### 2. Environment Variables

Vercel Dashboard → Project → Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://efi-api.onrender.com
```

### 3. Deploy

1. **Deploy** butonuna tıklayın
2. Build tamamlandıktan sonra URL'i kopyalayın
3. **Önemli**: Bu URL'i Render backend'deki `APP_BASE_URL` ve `CORS_ORIGINS`'e ekleyin

## ✅ Post-Deployment Checklist

- [ ] Backend API çalışıyor: `https://efi-api.onrender.com/health`
- [ ] Frontend çalışıyor: `https://your-frontend.vercel.app`
- [ ] Database seed edildi: Admin user oluşturuldu
- [ ] Magic link login test edildi
- [ ] Admin panel erişilebilir
- [ ] Worker logları kontrol edildi (Render dashboard'dan)
- [ ] Environment variables doğru set edildi
- [ ] CORS ayarları frontend URL'i içeriyor

## 🔧 Troubleshooting

### Backend başlamıyor
- Logları kontrol edin: Render Dashboard → Logs
- Environment variables eksik olabilir
- Database connection string yanlış olabilir

### Worker çalışmıyor
- Redis connection kontrol edin
- PYTHONPATH ayarlı mı kontrol edin
- Worker logs: Render Dashboard → Logs

### Frontend API çağrıları başarısız
- CORS ayarlarını kontrol edin
- `NEXT_PUBLIC_API_URL` doğru mu?
- Backend URL'i erişilebilir mi?

### Magic link email gelmiyor
- Resend API key doğru mu?
- `EMAIL_FROM` domain'i Resend'de verify edilmiş mi?
- Spam klasörünü kontrol edin

## 📝 Notlar

- Render free tier'da servisler 15 dakika idle sonrası sleep olur (ilk request yavaş olabilir)
- Production'da `JWT_SECRET` güçlü bir random string olmalı
- HTTPS kullanıldığında cookie `secure=True` olmalı (şu an `False` - production'da düzeltin)
- Database backup'ları düzenli alın
- Monitoring için Render'ın built-in monitoring'ini kullanın

## 🔐 Production Security Checklist

- [ ] `JWT_SECRET` güçlü ve unique
- [ ] Cookie `secure=True` (HTTPS için)
- [ ] CORS sadece frontend domain'i içeriyor
- [ ] Database connection SSL enabled
- [ ] Environment variables Render'da encrypted
- [ ] Admin email güvenli bir email adresi
- [ ] Rate limiting eklenmiş (opsiyonel ama önerilir)
