# engine.py
import asyncio
import logging
import re
import io
import time
import aiohttp
import matplotlib.pyplot as plt
from typing import Optional, Tuple
import google.generativeai as genai
from cachetools import TTLCache
from settings import *

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("membit-engine")

# --- CACHE & HTTP ---
cluster_cache = TTLCache(maxsize=256, ttl=10)

class SafeHTTP:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    async def ensure(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers={"User-Agent": "MembitContextAgent/77-AIOHTTP"})
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    async def get_json(self, url, headers=None, params=None, timeout=8, retries=2):
        await self.ensure()
        for attempt in range(retries+1):
            try:
                async with self.session.get(url, headers=headers, params=params, timeout=timeout) as resp:
                    if resp.status != 200:
                        await asyncio.sleep(0.25 * (attempt+1))
                        continue
                    return await resp.json()
            except Exception as e:
                logger.debug(f"Attempt {attempt+1} failed: {e}")
                await asyncio.sleep(0.25 * (attempt+1))
        return None

safe_http = SafeHTTP()

# --- GEMINI SETUP ---
model = None
if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-flash-latest")
    except Exception as e:
        logger.error(f"Gemini Init Error: {e}")

async def call_gemini_safe(prompt: str, max_tokens: int = 180):
    """Versi aman untuk akun gratisan"""
    if not model: return None, "AI Not Initialized"
    try:
        config = genai.types.GenerationConfig(max_output_tokens=max_tokens, temperature=0.4)
        resp = await asyncio.to_thread(model.generate_content, prompt, generation_config=config)
        if not resp.candidates: return None, "Blocked/Empty"
        return resp.text, ""
    except Exception as e:
        return None, str(e)

# --- MEMBIT LOGIC ---
async def fetch_clusters(keyword: str, limit: int = 6):
    key = f"clusters:{keyword}:{limit}"
    if key in cluster_cache: return cluster_cache[key]
    
    params = {"q": keyword, "limit": limit}
    data = await safe_http.get_json(CLUSTER_SEARCH_URL, headers=MEMBIT_HEADERS, params=params)
    
    if not data: return None
    clusters = data.get("clusters", [])[:limit]
    
    # Filter duplicates
    seen, unique = set(), []
    for c in clusters:
        lbl = c.get('label', '').strip().lower()
        if lbl not in seen:
            seen.add(lbl)
            unique.append(c)
            
    cluster_cache[key] = unique
    return unique

# --- HELPER UTILS ---
def compute_risk_score(text: str) -> int:
    t = (text or "").lower()
    score = 0
    for k, w in RISK_KEYWORDS.items():
        if k in t: score += w
    return max(0, min(100, score + 50))

def compute_color_from_score(score: int) -> int:
    if score >= 70: return 0xFF0000
    if score >= 40: return 0xFFD000
    return 0x00FF00

def get_recommendation_from_score(score: int) -> str:
    if score >= 70: return "🛑 High-risk indicators detected."
    if score >= 40: return "⚠️ Medium risk. Mixed signals."
    return "✅ Low/neutral risk. Looks generally safe."

def truncate(text, n=800):
    return text if len(text) <= n else text[:n-1] + "…"

def clean_text_summary(text: str) -> str:
    if not text: return ""
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'https?://\S+', '', text)
    return text.strip()

def generate_heuristic_insight(clusters: list) -> dict:
    if not clusters: return {"summary": "No data", "score": 50, "color": 0x00FF00, "recommendation": "Neutral"}
    combined = " ".join([c.get('summary','') for c in clusters])
    score = compute_risk_score(combined)
    return {
        "summary": "Topics: " + ", ".join([c.get('label','') for c in clusters[:5]]),
        "score": score,
        "color": compute_color_from_score(score),
        "recommendation": get_recommendation_from_score(score)
    }

# --- GRAPHING LOGIC ---
def generate_graph_sync(labels, values, keyword):
    try:
        buffer = io.BytesIO()
        plt.figure(figsize=(8,4)) 
        plt.plot(list(reversed(labels)), list(reversed(values)), marker="o", linestyle="--", color="#0099FF")
        plt.title(f"Engagement Trend — {keyword}")
        plt.xticks(rotation=15, ha='right', fontsize=8) 
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        plt.close()
        return buffer, None
    except Exception as e:
        return None, str(e)

