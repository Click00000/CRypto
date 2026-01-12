# 🎯 BAŞLANGIÇ - Exchange Flow Intelligence

## ✅ Sistem Hazır ve Production-Ready!

Tüm kod tamamlandı ve Vercel + Render'a deploy edilmeye hazır.

## 📚 Dokümantasyon Sırası

1. **Bu Dosya (START_HERE.md)** - Genel bakış
2. **QUICKSTART.md** - 5 dakikada canlıya alma
3. **DEPLOYMENT.md** - Detaylı deployment adımları
4. **README.md** - Teknik detaylar ve local development

## 🚀 Hızlı Başlangıç (3 Adım)

### 1. GitHub'a Push
```bash
cd exchange-flow-intelligence

# Otomatik script ile
chmod +x deploy.sh
./deploy.sh

# Veya manuel
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

### 2. Render Deploy (Backend + Worker)
- PostgreSQL database oluştur
- Redis instance oluştur  
- Backend web service deploy et
- Worker background service deploy et
- Detaylar: [QUICKSTART.md](./QUICKSTART.md)

### 3. Vercel Deploy (Frontend)
- GitHub repo'yu import et
- Root directory: `frontend`
- Environment variable: `NEXT_PUBLIC_API_URL`
- Detaylar: [QUICKSTART.md](./QUICKSTART.md)

## 📋 Gereksinimler

- GitHub hesabı
- Render hesabı (ücretsiz)
- Vercel hesabı (ücretsiz)
- Resend API key (email için)
- EVM RPC URL (Alchemy/Infura)
- Bitcoin Explorer API (Blockstream - ücretsiz)

## ⚙️ Önemli Environment Variables

### Backend (Render)
```
DATABASE_URL=<postgres-connection>
REDIS_URL=<redis-internal-url>
JWT_SECRET=<32+ karakter random string>
APP_BASE_URL=<vercel-frontend-url>
API_BASE_URL=<render-backend-url>
RESEND_API_KEY=<resend-key>
EMAIL_FROM=noreply@yourdomain.com
EVM_RPC_URL=<ethereum-rpc>
BTC_MODE=EXPLORER
BTC_EXPLORER_BASE_URL=https://blockstream.info/api
ADMIN_EMAIL=admin@yourdomain.com
CORS_ORIGINS=<vercel-frontend-url>
```

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=<render-backend-url>
```

## ✅ Post-Deployment Checklist

- [ ] Backend health check: `https://your-api.onrender.com/health`
- [ ] Frontend çalışıyor
- [ ] Database seed edildi
- [ ] Magic link login test edildi
- [ ] Admin panel erişilebilir
- [ ] Worker logları kontrol edildi

## 🎉 Başarılı!

Sistem canlıda çalışıyor. Admin panel'den exchange ve address ekleyerek başlayın!

## 🆘 Yardım

- **Hızlı Başlangıç**: [QUICKSTART.md](./QUICKSTART.md)
- **Detaylı Deployment**: [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Sorun Giderme**: [DEPLOYMENT.md](./DEPLOYMENT.md#-troubleshooting)

---

**🚀 Hadi başlayalım! QUICKSTART.md dosyasını açın ve 5 dakikada canlıya alın!**
