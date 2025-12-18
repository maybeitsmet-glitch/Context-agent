===================================================================
 CONTEXT AGENT V61+ — AI Crypto & Narrative Intelligence Bot
===================================================================
 Version: 1.0 (Hackathon Winner Edition)
 Language: Python 3.9+
 Author: V61 Team
===================================================================

[1] INTRODUCTION
-------------------------------------------------------------------
Thank you for purchasing Context Agent V61+.
This is a high-performance Discord bot that combines:
1. Membit API (Real-time narrative clusters)
2. Google Gemini AI (Contextual reasoning)
3. Matplotlib (Visual engagement graphs)

It is designed to be lightweight, modular, and crash-proof.

[2] PREREQUISITES
-------------------------------------------------------------------
Before you begin, ensure you have:
1. Python 3.9 or higher installed on your system/VPS.
2. A Discord Bot Token (from https://discord.com/developers).
3. A Membit API Key (from https://membit.ai).
4. A Google Gemini API Key (Optional, for AI features).

[3] INSTALLATION
-------------------------------------------------------------------
Step 1: Unzip the downloaded file.
Step 2: Open your terminal/command prompt in the bot folder.
Step 3: Install the required dependencies by running:

    pip install -r requirements.txt

[4] CONFIGURATION
-------------------------------------------------------------------
1. Create a new file named ".env" (without quotes) in the folder.
2. Open the ".env" file with a text editor (Notepad/VS Code).
3. Paste the following lines and fill in your keys:

    DISCORD_TOKEN=your_discord_bot_token_here
    MEMBIT_API_KEY=your_membit_api_key_here
    GEMINI_API_KEY=your_gemini_api_key_here
    COOLDOWN_SECONDS=12

4. Save the file.

[5] RUNNING THE BOT
-------------------------------------------------------------------
To start the bot, run this command in your terminal:

    python main.py

If successful, you will see: "✅ Bot Online: [BotName] | Mode: Modular V61+"

[6] COMMAND LIST
-------------------------------------------------------------------
!hunt <keyword>    -> Scan Membit clusters for a topic (e.g., !hunt bitcoin)
!graph <keyword>   -> Generate visual engagement chart (e.g., !graph election)
!analyze <text>    -> AI Sentiment analysis for any text.
!help              -> Show full command list.
!ping              -> Check bot latency.

[7] TROUBLESHOOTING / FAQ
-------------------------------------------------------------------
Q: I get a "429 Too Many Requests" error.
A: The bot has an auto-handler for this. It will wait and retry automatically.

Q: The graph is not showing text properly.
A: Ensure your server/VPS has a basic font installed. Matplotlib uses standard system fonts.

Q: AI commands are not working.
A: Check if your GEMINI_API_KEY is valid. If the API is down, the bot automatically switches to "Heuristic Mode" (local logic).

===================================================================
 END OF DOCUMENTATION
===================================================================
