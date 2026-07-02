# Deployment Guide — Vercel

## Overview

This project is deployed on **Vercel** with the following architecture:

- **Frontend (Next.js):** Native Vercel deployment
- **Backend (FastAPI):** Vercel Serverless Functions
- **Database:** Vercel Postgres (Neon) or Supabase (both support pgvector)
- **Domain:** Free Vercel subdomain (`*.vercel.app`)

## Prerequisites

1. **Vercel Account:** Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository:** Connected to Vercel
3. **Database:** Either Vercel Postgres or Supabase (see below)

## Step 1: Set Up Database

### Option A: Vercel Postgres (Neon)

1. Go to your Vercel project dashboard
2. Navigate to **Storage** → **Create Database** → **Postgres**
3. Select **Neon** as the provider
4. Choose a region close to your users
5. Click **Create**
6. Vercel will automatically add these environment variables:
   - `POSTGRES_URL`
   - `POSTGRES_URL_NO_SSL`
   - `POSTGRES_URL_NON_POOLING`
   - `POSTGRES_USER`
   - `POSTGRES_HOST`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DATABASE`

### Option B: Supabase (Alternative)

1. Sign up at [supabase.com](https://supabase.com)
2. Create a new project
3. Enable the **pgvector** extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. Copy the connection string from **Settings** → **Database**
5. Add to Vercel environment variables as `DATABASE_URL`

## Step 2: Configure Environment Variables

In your Vercel project dashboard, go to **Settings** → **Environment Variables** and add:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# DeepSeek AI
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Auth
AUTH_SECRET=your_32_char_random_string_here
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD_HASH=$2b$12$... (generate with scripts/gen_password_hash.py)

# CORS
CORS_ORIGINS=https://your-project.vercel.app

# Optional: Public identity (if not using API)
NEXT_PUBLIC_OWNER_NAME=Your Name
NEXT_PUBLIC_OWNER_EMAIL=your.email@example.com
NEXT_PUBLIC_GITHUB_URL=https://github.com/yourusername
NEXT_PUBLIC_LINKEDIN_URL=https://linkedin.com/in/yourusername
```

## Step 3: Deploy Frontend

1. In Vercel dashboard, click **Add New** → **Project**
2. Import your GitHub repository
3. Configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
4. Click **Deploy**

## Step 4: Deploy Backend

1. In the same Vercel project, add a new function:
   - Navigate to **Settings** → **Functions**
   - Or use the Vercel CLI: `vercel deploy --prod`
2. The backend will be available at `/api/*` routes

## Step 5: Run Database Migrations

After deployment, run migrations to create tables:

```bash
# Using Vercel CLI
vercel env pull .env.local
cd backend
alembic upgrade head

# Or connect directly to your database
DATABASE_URL=... alembic upgrade head
```

## Step 6: Verify Deployment

1. **Frontend:** Visit `https://your-project.vercel.app`
2. **Backend Health:** Visit `https://your-project.vercel.app/api/health`
3. **Admin Panel:** Visit `https://your-project.vercel.app/adshs/login`
4. **Chat:** Visit `https://your-project.vercel.app/chat`

## Step 7: Create Admin Account

Generate a password hash:

```bash
cd backend
python scripts/gen_password_hash.py your_secure_password
```

Update `ADMIN_PASSWORD_HASH` in Vercel environment variables and redeploy.

## Monitoring & Logs

- **Frontend Logs:** Vercel Dashboard → **Deployments** → Select deployment → **Functions**
- **Backend Logs:** Same as above, filter by `/api/*` routes
- **Database:** Neon/Supabase dashboard

## Limitations & Considerations

### Vercel Serverless Functions

- **Cold Start:** 1-3 seconds on first request after idle
- **Timeout:** 10 seconds (Hobby) / 60 seconds (Pro)
- **Memory:** 1024 MB (Hobby) / 3008 MB (Pro)
- **No Persistent Connections:** Each request is a new function instance

### Database

- **Vercel Postgres (Neon):** Free tier includes 0.5 GB storage, 190 compute hours/month
- **Supabase:** Free tier includes 500 MB database, 50,000 monthly active users
- **pgvector:** Both support pgvector for RAG embeddings

### Cost Estimate (Hobby Plan)

- **Vercel:** Free (Hobby plan)
- **Database:** Free tier sufficient for personal portfolio
- **DeepSeek API:** Pay-per-use (~$0.14 per 1M tokens)

## Troubleshooting

### Backend returns 500 errors

- Check environment variables are set correctly
- Verify `DATABASE_URL` is accessible from Vercel
- Check function logs for Python errors

### Database connection fails

- Ensure database allows connections from Vercel IP ranges
- Check if `pgvector` extension is enabled
- Verify connection string format

### Cold start is too slow

- Consider upgrading to Vercel Pro for faster cold starts
- Use connection pooling (Neon provides this by default)
- Optimize Python imports in `api/index.py`

## Custom Domain (Optional)

1. Go to **Settings** → **Domains**
2. Add your custom domain
3. Configure DNS records as instructed
4. Vercel will automatically provision SSL certificate

## Rollback

If something goes wrong:

1. Go to **Deployments** in Vercel dashboard
2. Find the last working deployment
3. Click **Promote to Production**

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Neon Documentation](https://neon.tech/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
