# Bakhmach Business Hub - Quick Start Guide

**Get up and running with Bakhmach Business Hub in 15 minutes!**

## 📋 Prerequisites

- Node.js 18+ ([Download](https://nodejs.org/))
- npm or yarn
- PostgreSQL 13+ ([Download](https://www.postgresql.org/))
- Git

## 🚀 Step 1: Clone the Repository

```bash
git clone https://github.com/romanchaa997/Bakhmach-Business-Hub.git
cd Bakhmach-Business-Hub
```

## 🏗️ Step 2: Set Up the Backend

```bash
cd backend
npm install
cp env.template .env
```

Edit `.env` with your configuration:

```env
NODE_ENV=development
PORT=3001
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bakhmach_hub
DB_USER=postgres
DB_PASSWORD=your_password
JWT_SECRET=your_secret_key
CORS_ORIGIN=http://localhost:3000
```

## 💾 Step 3: Initialize Database

```bash
# Create database
psql -U postgres -c "CREATE DATABASE bakhmach_hub;"

# Run schema
psql -U postgres -d bakhmach_hub -f schema.sql
```

## ▶️ Step 4: Start Backend Server

```bash
npm run dev
```

Server running at: `http://localhost:3001`

## 🎨 Step 5: Set Up Frontend (Optional)

```bash
cd ../frontend  # if it exists
npm install
npm start
```

Frontend running at: `http://localhost:3000`

## 📱 Step 6: Test the API

### Health Check

```bash
curl http://localhost:3001/api/v1/health
```

### Register User

```bash
curl -X POST http://localhost:3001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "name": "User Name"
  }'
```

### Login

```bash
curl -X POST http://localhost:3001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

## 🔍 Step 7: Explore the Architecture

1. **View Architecture Model:**
   - Open `docs/ARCHITECTURE.json` for complete system design

2. **Interactive Visualizer:**
   - Open `docs/ARCHITECTURE-VISUALIZER.html` in your browser

3. **API Endpoints:**
   - Check `backend/routes.ts` for all available endpoints

## 📚 Available Commands

### Backend

```bash
# Development (with hot reload)
npm run dev

# Build TypeScript
npm run build

# Production
npm start

# Tests
npm test

# Linting
npm run lint
```

## 🐛 Troubleshooting

### Database Connection Failed

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Or check if port 5432 is in use
lsof -i :5432
```

### Port Already in Use

```bash
# Change PORT in .env file
PORT=3002  # Use different port

# Or kill process on port 3001
lsof -i :3001 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Module Not Found

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📖 Next Steps

1. **Read Documentation:**
   - `docs/README.md` - Documentation hub
   - `docs/DEV-REVIEW.md` - Technical review
   - `docs/ARCHITECTURE.json` - System design

2. **Create Your First PDP:**
   ```bash
   curl -X POST http://localhost:3001/api/v1/pdps/create \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "My Development Plan",
       "description": "Learning backend development",
       "startDate": "2026-01-02",
       "endDate": "2026-12-31"
     }'
   ```

3. **Explore Features:**
   - Goals Management
   - Task Tracking
   - Analytics
   - Consciousness Metrics

## 🤝 Contributing

See `CONTRIBUTING.md` for guidelines.

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/romanchaa997/Bakhmach-Business-Hub/issues)
- **Email:** roman@bakhmach-hub.com
- **Documentation:** See `/docs` directory

## 📝 Project Structure

```
Bakhmach-Business-Hub/
├── backend/                    # Node.js/Express API
├── frontend/                   # React web app (if exists)
├── services/                   # Microservices
├── docs/                       # Documentation
│   ├── README.md              # Doc hub
│   ├── QUICK-START.md         # This file
│   ├── ARCHITECTURE.json      # System design
│   ├── DEV-REVIEW.md          # Technical review
│   └── ...
├── package.json
└── README.md
```

## ⚡ Quick Reference

| Command | Purpose |
|---------|----------|
| `npm run dev` | Start development server |
| `npm test` | Run tests |
| `npm run build` | Build for production |
| `npm run lint` | Check code quality |

## 🎯 Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/auth/profile` | Get profile |
| POST | `/api/v1/pdps/create` | Create PDP |
| GET | `/api/v1/pdps` | List PDPs |
| POST | `/api/v1/goals/create` | Create goal |
| GET | `/api/v1/goals` | List goals |
| POST | `/api/v1/tasks/create` | Create task |
| GET | `/api/v1/tasks` | List tasks |

---

**Ready to build? Happy coding!** 🚀

*Last Updated: January 2, 2026*
*Version: 1.0*
