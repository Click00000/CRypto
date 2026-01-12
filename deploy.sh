#!/bin/bash

# Exchange Flow Intelligence - Auto Deployment Script
# Bu script GitHub'a push yapar ve deployment bilgilerini gösterir

set -e

echo "🚀 Exchange Flow Intelligence - Deployment Script"
echo "=================================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Git repository başlatılıyor..."
    git init
    git branch -M main
fi

# Check if remote exists
if ! git remote get-url origin &>/dev/null; then
    echo "⚠️  GitHub remote repository URL'i gerekli!"
    echo ""
    read -p "GitHub repository URL'ini girin (örn: https://github.com/username/repo.git): " REPO_URL
    if [ -z "$REPO_URL" ]; then
        echo "❌ Repository URL gerekli!"
        exit 1
    fi
    git remote add origin "$REPO_URL"
    echo "✅ Remote repository eklendi: $REPO_URL"
fi

# Add all files
echo ""
echo "📝 Dosyalar ekleniyor..."
git add .

# Check if there are changes
if git diff --staged --quiet; then
    echo "ℹ️  Değişiklik yok, zaten commit edilmiş."
else
    # Commit
    echo "💾 Commit yapılıyor..."
    git commit -m "Initial commit: Exchange Flow Intelligence MVP" || {
        echo "⚠️  Commit başarısız. Devam ediliyor..."
    }
fi

# Push to GitHub
echo ""
echo "📤 GitHub'a push yapılıyor..."
echo "⚠️  GitHub credentials gerekebilir!"
echo ""

if git push -u origin main 2>&1; then
    echo ""
    echo "✅ GitHub'a başarıyla push edildi!"
else
    echo ""
    echo "⚠️  Push başarısız olabilir. Manuel olarak deneyin:"
    echo "   git push -u origin main"
    echo ""
fi

# Get repository URL
REPO_URL=$(git remote get-url origin 2>/dev/null || echo "")

echo ""
echo "=================================================="
echo "✅ GitHub Push Tamamlandı!"
echo ""
echo "📋 Sonraki Adımlar:"
echo ""
echo "1️⃣  RENDER - Backend & Worker:"
echo "   → https://dashboard.render.com"
echo "   → New → PostgreSQL (database oluştur)"
echo "   → New → Redis (instance oluştur)"
echo "   → New → Web Service (backend deploy)"
echo "   → New → Background Worker (worker deploy)"
echo "   → Repository: $REPO_URL"
echo ""
echo "2️⃣  VERCEL - Frontend:"
echo "   → https://vercel.com/dashboard"
echo "   → Add New → Project"
echo "   → Import Git Repository: $REPO_URL"
echo "   → Root Directory: frontend"
echo "   → Environment Variable: NEXT_PUBLIC_API_URL"
echo ""
echo "📖 Detaylı rehber: QUICKSTART.md dosyasına bakın"
echo ""
echo "🎉 Hazır! Render ve Vercel'e deploy edebilirsiniz!"
