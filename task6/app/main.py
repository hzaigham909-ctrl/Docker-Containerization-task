"""
TASK 6: DISTRIBUTED FULL-STACK DEPLOYMENT
-----------------------------------------
Description: Orchestration of a production-ready sentiment analysis 
stack using Docker Compose for environment synchronization.

Features: 
- Reverse Proxy: Nginx configuration for request routing.
- Performance: Redis integration for inference caching.
- Persistence: PostgreSQL logging for prediction history.
- Scalability: Multi-container architecture with FastAPI.

Stack: Docker Compose, Nginx, Redis, PostgreSQL, FastAPI.
"""


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from textblob import TextBlob
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
import time

app = FastAPI()

#____Database connection (PostgreSQL)_____
def get_db_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST","db"),
        database=os.getenv("POSTGRES_DB","sentiment_db"),
        user=os.getenv("POSTGRES_USER","user"),
        password=os.getenv("POSTGRES_PASSWORD","password"),
    )

#_____Redis connection_________
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST","redis"),
    port=6379,
    db=0,
    decode_responses=True
) 

class TextInput(BaseModel):
    text:str

@app.post("/analyze")
def analyze_sentiment(input:TextInput):
    text = input.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Text is required") 
    
#________Check cache____________
    cache_key=f"sentiment:{text}"
    cache_result=redis_client.get(cache_key)
    if cache_result:
        result = json.loads(cache_result)
        log_to_db(text,result,from_cache=True)
        return result
    

#_______Perform Sentiments analysis_______
    blob=TextBlob(text)
    polarity=blob.sentiment.polarity
    if polarity >0:
        sentiment = "Positive"
    elif polarity<0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    result = {"sentiment":sentiment,"score":polarity}

#______Cache Result (expire in 1 hour)_______
    redis_client.set(cache_key,json.dumps(result),ex=3600)

#________Log to database_________________
    log_to_db(text , result,from_cache=False)

    return result


def log_to_db(text:str,result:dict,from_cache:bool):
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            """INSERT INTO sentiment_logs (text, sentiment, score, from_cache, timestamp)
            VALUES (%s, %s, %s, %s, %s)""",(text,result["sentiment"],result["score"],from_cache,time.time()))
        conn.commit()
        return result
    except Exception as e:
        print(f"Logging error: {e}")

    finally:
        cur.close()
        conn.close()


#____________Get Method___________________

@app.get("/get")
def health():
    for attempt in range(5):
        try:
            conn = get_db_conn()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM sentiment_logs")
            total = cur.fetchone()[0]
            
            cur.execute("""
                SELECT text, sentiment 
                FROM sentiment_logs 
                ORDER BY timestamp DESC 
                LIMIT 5
            """)
            recent = cur.fetchall()
            
            cur.close()
            conn.close()
            
            return {
                "status": "healthy",
                "total_logs": total,
                "recent": recent
            }
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(3)   # wait 3 seconds before retry
    raise HTTPException(status_code=503, detail="Database not ready after retries")

@app.get("/")
def root():
    return {
        "message": "Sentiment Analysis API is running!",
        "endpoints": {
            "analyze": "POST /analyze with {'text': 'your sentence'}",
            "health": "GET /get",
            "docs": "GET /docs (Swagger UI)"
        }
    }