import sqlite3,time
import numpy as np
from fastapi import FastAPI
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")


app = FastAPI()
agent = OpenAI(api_key=api_key, base_url=base_url)

raw = open("十句话.txt", encoding="utf-8").read()
CHUNKS = [p.strip() for p in raw.split("\n") if p.strip()]
VECS = [d.embedding for d in agent.embeddings.create(
    model="qwen3.7-text-embedding", input=CHUNKS).data]

def sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

conn = sqlite3.connect("data.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
conn.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        q TEXT,
        a TEXT
    )
    """)
conn.commit()

@app.get("/ask")
def ask(q: str):
    q_vec = agent.embeddings.create(
        model="qwen3.7-text-embedding", input=q).data[0].embedding

    scored = [(sim(q_vec, v), t) for v, t in zip(VECS, CHUNKS)]
    scored.sort(key=lambda x: x[0], reverse=True)
    ctx = "\n".join(t for s, t in scored[:3])

    resp = agent.chat.completions.create(
        model="qwen3.8-flash",
        messages=[
            {"role": "system", "content": "只根据资料回答。资料里没有的，直接说不知道。"},
            {"role": "user", "content": f"资料：\n{ctx}\n\n问题：{q}"},
        ],
    )
    answer = resp.choices[0].message.content

    conn.execute(
        "INSERT INTO logs (ts, q, a) VALUES (?, ?, ?)",
        (time.strftime("%Y-%m-%d %H:%M:%S"), q, answer),
    )
    conn.commit()

    return {
        "answer": answer,
        "sources": [t for s, t in scored[:3]],
    }

@app.get("/history")
def history():
    rows = conn.execute(
        "SELECT ts, q, a FROM logs ORDER BY rowid DESC LIMIT 10"
    ).fetchall()
    return {"rows": [dict(r) for r in rows]}




