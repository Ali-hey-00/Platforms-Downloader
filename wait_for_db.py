#!/usr/bin/env python
import os
import time
import psycopg2
from urllib.parse import urlparse

def wait_for_db():
    """Wait for database to be available"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")

    # Parse database URL
    url = urlparse(db_url)
    dbname = url.path[1:]
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port or 5432

    # Maximum number of retries
    max_retries = 30
    retry_interval = 2

    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            conn.close()
            print("Database is ready!")
            return
        except psycopg2.OperationalError as e:
            print(f"Database not ready (attempt {i + 1}/{max_retries}). Retrying...")
            time.sleep(retry_interval)

    raise Exception("Could not connect to database after multiple attempts")

if __name__ == "__main__":
    wait_for_db()