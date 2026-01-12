# 🔧 Render Worker Manuel Kurulum (Free Plan)

Render'ın free plan'ında background worker desteklenmiyor. Worker'ı manuel olarak oluşturmanız gerekiyor.

## 📋 Adımlar

### 1. Backend API Deploy Edildikten Sonra

### 2. Worker Oluştur

1. **Render Dashboard** → **New** → **Background Worker**
2. **Connect GitHub**: `Click00000/CRypto` repo'sunu seçin
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

### 3. Environment Variables

Backend API ile aynı environment variables'ları ekleyin:

```
DATABASE_URL=<backend-api'den kopyala>
REDIS_URL=<backend-api'den kopyala>
JWT_SECRET=<backend-api'den kopyala veya yeni oluştur>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168
APP_BASE_URL=<vercel-frontend-url>
API_BASE_URL=<render-backend-url>
RESEND_API_KEY=<resend-key>
EMAIL_FROM=noreply@yourdomain.com
EVM_RPC_URL=<ethereum-rpc>
BTC_MODE=EXPLORER
BTC_EXPLORER_BASE_URL=https://blockstream.info/api
ADMIN_EMAIL=<admin-email>
CORS_ORIGINS=<vercel-frontend-url>
```

**Not**: Backend API'deki environment variables'ları kopyalayıp yapıştırabilirsiniz.

### 4. Deploy

**Create Background Worker** butonuna tıklayın.

## ⚠️ Önemli Not

Free plan'da background worker'lar **15 dakika idle sonrası sleep olur**. Production için paid plan önerilir.

## ✅ Kontrol

Worker deploy edildikten sonra:
- Logları kontrol edin: Render Dashboard → Worker → Logs
- Celery worker ve beat çalışıyor mu kontrol edin

---

**Alternatif**: Eğer free plan kullanıyorsanız, worker'ı web service olarak da deploy edebilirsiniz (ama ideal değil).
