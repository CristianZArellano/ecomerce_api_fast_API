#!/bin/bash

# E-commerce API Production Start Script
# =====================================

set -e  # Exit on any error

echo "🚀 Starting E-commerce API..."

# Set default values if not provided
export APP_ENV=${APP_ENV:-production}
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}
export WORKERS=${WORKERS:-4}

echo "📊 Environment: $APP_ENV"
echo "🌐 Host: $HOST:$PORT"
echo "⚡ Workers: $WORKERS"

# Wait for database to be ready
echo "⏳ Waiting for database..."
python -c "
import asyncio
import asyncpg
import os
import sys
import time

async def wait_for_db():
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Try to connect to the database
            conn = await asyncpg.connect(
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD'),
                database=os.getenv('POSTGRES_DB'),
                host=os.getenv('POSTGRES_HOST'),
                port=os.getenv('POSTGRES_PORT')
            )
            await conn.close()
            print('✅ Database is ready!')
            return
        except Exception as e:
            retry_count += 1
            print(f'⏳ Database not ready (attempt {retry_count}/{max_retries}): {e}')
            await asyncio.sleep(2)
    
    print('❌ Database connection failed after all retries')
    sys.exit(1)

asyncio.run(wait_for_db())
"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
python -c "
import redis
import os
import sys
import time

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        r = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
        r.ping()
        print('✅ Redis is ready!')
        break
    except Exception as e:
        retry_count += 1
        print(f'⏳ Redis not ready (attempt {retry_count}/{max_retries}): {e}')
        time.sleep(2)
else:
    print('❌ Redis connection failed after all retries')
    sys.exit(1)
"

# Run database migrations if needed
echo "🔄 Running database setup..."
python -c "
import asyncio
from app.database import engine, Base

async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ Database tables ready!')

asyncio.run(setup_database())
"

# Start the application
echo "🚀 Starting FastAPI server..."

if [ "$APP_ENV" = "development" ]; then
    # Development mode with hot reload
    exec uvicorn main:app --host $HOST --port $PORT --reload --log-level debug
else
    # Production mode with multiple workers
    exec uvicorn main:app \
        --host $HOST \
        --port $PORT \
        --workers $WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        --log-level info \
        --access-log \
        --use-colors \
        --loop uvloop \
        --http httptools
fi