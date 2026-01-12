# Exchange Flow Intelligence

Production-ready MVP for tracking exchange wallet flows on EVM chains and Bitcoin.

**🚀 Hızlı Deployment**: [QUICKSTART.md](./QUICKSTART.md) - 5 dakikada canlıya alın!  
**📖 Detaylı Deployment**: [DEPLOYMENT.md](./DEPLOYMENT.md) - Tüm adımlar

## 🏗️ Architecture

- **Frontend**: Next.js 14 (App Router) → Vercel
- **Backend API**: FastAPI → Render
- **Worker**: Celery + Redis → Render
- **Database**: PostgreSQL (Render managed)
- **Cache/Queue**: Redis (Render managed)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional, for local dev)
- PostgreSQL 14+ (or use Docker)
- Redis 7+ (or use Docker)

### Local Development

#### Option 1: Docker Compose (Recommended)

1. **Clone and setup**:
```bash
cd exchange-flow-intelligence
# Create .env file in backend/ directory
cd backend
cp .env.example .env
# Edit .env with your configuration (at minimum: DATABASE_URL, REDIS_URL, JWT_SECRET, ADMIN_EMAIL)
```

2. **Start all services**:
```bash
cd ..  # Back to root
docker-compose up -d
```

3. **Run migrations and seed**:
```bash
docker-compose exec api alembic upgrade head
docker-compose exec api python scripts/seed.py
```

4. **Access**:
- Frontend: http://localhost:3000 (if running separately, see Option 2)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

#### Option 2: Manual Setup

1. **Start database and Redis**:
```bash
docker-compose up -d postgres redis
# Or use your own PostgreSQL/Redis instances
```

2. **Backend setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Seed database
python scripts/seed.py

# Start backend
uvicorn app.main:app --reload --port 8000
```

3. **Worker setup** (in separate terminal):
```bash
cd worker
source venv/bin/activate  # Use same venv or create new one
pip install -r requirements.txt

# Set PYTHONPATH to include backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)/../backend"

# Start worker + beat
celery -A app.celery_app worker --loglevel=info &
celery -A app.celery_app beat --loglevel=info
```

4. **Frontend setup** (in separate terminal):
```bash
cd frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
```

5. **Access**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📦 Project Structure

```
exchange-flow-intelligence/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Config, security, dependencies
│   │   ├── db/       # Database models, session
│   │   ├── services/ # Business logic
│   │   └── ingestion/ # EVM/BTC adapters
│   ├── alembic/      # Database migrations
│   └── scripts/      # Seed scripts
├── frontend/         # Next.js application
│   ├── app/          # App Router pages
│   ├── components/   # React components
│   └── lib/          # Utilities, API client
├── worker/           # Celery worker
│   └── app/
│       └── tasks/    # Background jobs
└── shared/           # Shared types/utilities (optional)
```

## 🔐 Authentication

1. Go to `/login`
2. Enter your email
3. Check "Send me updates" for marketing opt-in
4. Check your email for magic link
5. Click link → auto-login → redirect to dashboard

**Admin Access**: Set `ADMIN_EMAIL` in `.env` and use that email to login. First login creates admin user.

## 📊 Admin Panel

Access `/admin` (requires admin role):

- **Exchanges**: Create/edit exchanges (Binance, Coinbase, etc.)
- **Addresses**: Add labeled addresses (hot/cold/deposit/reserve) for EVM or BTC
- **Sync State**: View last processed block/height, trigger resync

## 🔄 Ingestion

### EVM Chains

Configure `EVM_RPC_URL` in `.env`. Worker automatically:
- Follows blocks incrementally
- Tracks native ETH transfers
- Parses ERC20 Transfer events
- Records transfers involving labeled addresses

### Bitcoin

Choose mode in `.env`:
- `BTC_MODE=CORE_RPC`: Use Bitcoin Core RPC
- `BTC_MODE=EXPLORER`: Use Explorer API

Worker tracks transactions involving labeled addresses.

## 📈 Metrics & Alerts

- **Flow Metrics**: Aggregated by exchange, asset, time window (1h, 1d)
- **Alerts**: Z-score anomaly detection (threshold: |z| >= 3)

Access via:
- `GET /exchanges/{id}/flows`
- `GET /alerts/live`

## 🚢 Deployment

### Backend (Render)

1. Create new Web Service
2. Connect GitHub repo
3. Build Command: `cd backend && pip install -r requirements.txt`
4. Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables (see `.env.example`)
6. Add PostgreSQL database (Render managed)
7. Add Redis instance (Render managed)
8. Run migrations: `cd backend && alembic upgrade head`
9. Run seed: `cd backend && python scripts/seed.py`

### Worker (Render)

1. Create new Background Worker
2. Connect same repo
3. Build Command: `cd worker && pip install -r requirements.txt`
4. Start Command: `cd worker && celery -A app.celery_app worker --loglevel=info`
5. Add same environment variables
6. (Optional) Create second worker for beat: `celery -A app.celery_app beat --loglevel=info`

### Frontend (Vercel)

1. Import project from GitHub
2. Root Directory: `frontend`
3. Build Command: `npm run build`
4. Output Directory: `.next`
5. Add Environment Variables:
   - `NEXT_PUBLIC_API_URL`: Your Render backend URL

## 🧪 Testing

### Quick Ingestion Test

1. Add a test exchange via admin panel
2. Add a test address (use a known active address)
3. Trigger manual sync: `POST /admin/jobs/resync`
4. Check `GET /admin/sync-state` for progress
5. View flows: `GET /exchanges/{id}/flows`

### Unit Tests

```bash
cd backend
pytest tests/
```

## 📝 Environment Variables

See `.env.example` for all required variables.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET`: Secret for JWT signing
- `APP_BASE_URL`: Frontend URL (for email links)
- `API_BASE_URL`: Backend URL
- `RESEND_API_KEY`: Resend API key for emails
- `EVM_RPC_URL`: Ethereum JSON-RPC endpoint
- `BTC_MODE`: `CORE_RPC` or `EXPLORER`
- `ADMIN_EMAIL`: Email for default admin user

## 🔧 Development

### Adding New Exchange Addresses

1. Login as admin
2. Go to `/admin/exchanges` → Create or select exchange
3. Go to `/admin/addresses` → Add address
4. Set chain (EVM or BTC), label (hot/cold/deposit/reserve)
5. Worker will start tracking automatically

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 📄 License

MIT
