import discord
import os
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 檢查 TOKEN 是否成功載入
if TOKEN is None:
    print("Error: DISCORD_TOKEN not found. Please make sure your .env file is configured correctly.")
    exit()

intents = discord.Intents.all()
client = discord.Client(command_prefix="!", intents=intents)


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("hi"):
        await message.channel.send("Hello!")


client.run(TOKEN)
