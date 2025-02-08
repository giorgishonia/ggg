import os
import discord
import random
import aiohttp
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GIPHY_API_KEY = "RgmLtSLLbxzbmd1Db4m4aqOppy102tP3"
CHANNEL_ID = 1315209735393247293  # Target channel ID

# Bot setup with minimal intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Global variables
current_topic = "random"
is_sending_gifs = True

# Expanded list of random topics
RANDOM_TOPICS = [
    # Entertainment
    "funny", "memes", "fails", "comedy", "jokes", "humor", "laugh", "entertainment",
    "movies", "tv shows", "anime", "cartoons", "gaming", "video games", "sports",
    "dance", "music", "concerts", "party", "celebration",
    
    # Animals
    "cats", "dogs", "puppies", "kittens", "animals", "cute animals", "pets",
    "wildlife", "birds", "pandas", "foxes", "hamsters", "penguins", "otters",
    
    # Reactions
    "wow", "omg", "awesome", "amazing", "cool", "mindblown", "excited", "happy",
    "sad", "angry", "confused", "facepalm", "eyeroll", "thumbsup", "applause",
    
    # Pop Culture
    "trending", "viral", "popular", "celebrities", "movies", "tv shows",
    "superheros", "disney", "marvel", "star wars", "harry potter",
    
    # Activities
    "sports", "football", "basketball", "soccer", "baseball", "gaming",
    "cooking", "food", "art", "music", "dance", "skateboarding", "surfing",
    
    # Nature
    "nature", "landscapes", "ocean", "mountains", "forests", "sunsets",
    "weather", "space", "stars", "universe", "science",
    
    # Technology
    "technology", "computers", "robots", "future", "science", "innovation",
    "gadgets", "phones", "gaming", "virtual reality",
    
    # Emotions
    "love", "happiness", "excitement", "surprise", "joy", "peace",
    "motivation", "inspiration", "success", "celebration",
    
    # Internet Culture
    "memes", "viral", "trending", "social media", "influencers", "tiktok",
    "youtube", "streaming", "gaming", "esports",
    
    # Miscellaneous
    "magic", "illusions", "art", "creativity", "design", "fashion",
    "beauty", "fitness", "adventure", "travel", "food", "cooking",
    
    # Actions
    "jumping", "running", "dancing", "flying", "swimming", "sleeping",
    "eating", "singing", "playing", "working", "exercising",
    
    # Seasonal
    "summer", "winter", "spring", "fall", "holidays", "christmas",
    "halloween", "new year", "birthday", "vacation"
]

async def get_gif(topic=None):
    """Fetch a GIF URL from Giphy API for any topic."""
    if topic == "random" or topic is None:
        search_topic = random.choice(RANDOM_TOPICS)
    else:
        search_topic = topic

    url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={search_topic}&limit=25&rating=pg-13"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None, None
            
            data = await response.json()
            if not data["data"]:
                return None, None
            
            gif_url = random.choice(data["data"])["images"]["original"]["url"]
            return search_topic, gif_url

@bot.event
async def on_ready():
    """Bot startup event."""
    print(f"✅ Logged in as {bot.user.name}")
    send_gif.start()  # Start the scheduled task

@bot.command(name="gifs")
async def set_gif_topic(ctx, *, topic="random"):
    """Command to set GIF topic or control gif sending."""
    global current_topic, is_sending_gifs
    
    if topic.lower() == "stop":
        is_sending_gifs = False
        await ctx.send("🛑 Stopped sending GIFs!")
        return
    elif topic.lower() == "start":
        is_sending_gifs = True
        await ctx.send("▶️ Started sending GIFs!")
        return
    
    current_topic = topic.lower()
    await ctx.send(f"🔄 Changed GIF topic to: {current_topic}")

    # Send an immediate example GIF
    topic, gif_url = await get_gif(current_topic)
    if gif_url:
        embed = discord.Embed(title=f"Theme: {topic}", color=discord.Color.random())
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ Couldn't find any GIFs for: {topic}")

@tasks.loop(minutes=1)
async def send_gif():
    """Send a GIF to the specified channel every minute."""
    if not is_sending_gifs:
        return

    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        topic, gif_url = await get_gif(current_topic)
        if gif_url:
            embed = discord.Embed(title=f"Theme: {topic}", color=discord.Color.random())
            embed.set_image(url=gif_url)
            await channel.send(embed=embed)
        else:
            print(f"❌ Failed to fetch GIF for topic: {current_topic}")

# Run the bot
bot.run(DISCORD_TOKEN)