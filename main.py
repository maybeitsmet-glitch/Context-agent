# main.py
import discord
import asyncio
import time
from settings import *
import engine  # Import file engine.py tadi

# Discord Setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Cooldown Tracker
user_last_call = {}

def check_cooldown(user_id):
    last = user_last_call.get(user_id, 0)
    if int(time.time()) - last < COOLDOWN_SECONDS:
        return False
    user_last_call[user_id] = int(time.time())
    return True

@client.event
async def on_ready():
    print(f"✅ Bot Online: {client.user} | Mode: Modular V61+")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Membit Data • !help"))

# --- HANDLERS ---
async def handle_hunt(channel, keyword):
    await channel.send(f"🔎 Hunting Membit for **{keyword}**...")
    clusters = await engine.fetch_clusters(keyword)
    
    if not clusters:
        await channel.send("❌ No clusters found or API error.")
        return

    insight = engine.generate_heuristic_insight(clusters)
    
    # Create Embed
    embed = discord.Embed(
        title=f"Membit Hunt: {keyword}",
        description=insight['recommendation'],
        color=insight['color']
    )
    embed.add_field(name="Heuristic Insight", value=engine.truncate(insight['summary'], 900), inline=False)
    
    for c in clusters[:3]: # Show top 3
        summary = engine.clean_text_summary(c.get("summary", ""))
        embed.add_field(name=f"🔹 {c.get('label')}", value=engine.truncate(summary, 500), inline=False)
        
    embed.set_footer(text=HACKATHON_FOOTER)
    await channel.send(embed=embed)

async def handle_graph(channel, keyword):
    await channel.send(f"📊 Generating Graph for **{keyword}**...")
    clusters = await engine.fetch_clusters(keyword, limit=8)
    
    if not clusters:
        await channel.send("⚠️ No data to graph.")
        return

    labels = [c.get("label", "N/A") for c in clusters]
    values = [float(c.get("engagement_score") or 0) for c in clusters]
    
    buffer, err = await asyncio.to_thread(engine.generate_graph_sync, labels, values, keyword)
    
    if err:
        await channel.send(f"⚠️ Graph Error: {err}")
        return

    file = discord.File(fp=buffer, filename="graph.png")
    embed = discord.Embed(title=f"Engagement Graph: {keyword}", color=0x3BA3FF)
    embed.set_image(url="attachment://graph.png")
    await channel.send(file=file, embed=embed)

async def handle_analyze(channel, text):
    await channel.send("🧠 AI Analyzing Sentiment...")
    prompt = f"Analyze sentiment briefly (Positive/Negative/Neutral):\n{text}"
    resp, err = await engine.call_gemini_safe(prompt)
    
    if err: resp = "⚠️ AI Unavailable (Using Fallback logic)."
    
    embed = discord.Embed(title="AI Analysis", description=resp, color=0x00CC99)
    await channel.send(embed=embed)

# --- MAIN LOOP ---
@client.event
async def on_message(message):
    if message.author == client.user or not message.content.startswith("!"):
        return

    uid = message.author.id
    parts = message.content.split()
    cmd = parts[0]
    args = " ".join(parts[1:])

    if cmd in COMMANDS_WITH_COOLDOWN:
        if not check_cooldown(uid):
            await message.channel.send(f"⏳ Cooldown! Wait {COOLDOWN_SECONDS}s.")
            return

    try:
        if cmd == "!hunt" and args:
            await handle_hunt(message.channel, args)
        elif cmd == "!graph" and args:
            await handle_graph(message.channel, args)
        elif cmd == "!analyze" and args:
            await handle_analyze(message.channel, args)
        elif cmd == "!ping":
            await message.channel.send("Pong! 🏓")
        elif cmd == "!help":
            await message.channel.send("Commands: `!hunt <topic>`, `!graph <topic>`, `!analyze <text>`")
            
    except Exception as e:
        await message.channel.send(f"⚠️ Error: {e}")

# Run Bot
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ Error: DISCORD_TOKEN not found in .env")
    else:
        try:
            client.run(DISCORD_TOKEN)
        finally:
            asyncio.run(engine.safe_http.close())

