import discord
import os
import json
import io
import aiohttp
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

# 載入 .env 檔案中的環境變數
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
REST_API = os.getenv("PALWORLD_API_BASE_URL")

# 檢查 TOKEN 是否成功載入
if TOKEN is None:
    print(
        "Error: DISCORD_TOKEN not found. Please make sure your .env file is configured correctly."
    )
    exit()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


# Bot login information
@bot.event
async def on_ready():
    slash = await bot.tree.sync()
    print(f"登入身份: {bot.user}")
    print(f"載入 {len(slash)} 個斜線指令")


@bot.tree.command(name="hello", description="Hello, world!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello, world!")


# @bot.tree.command(name="ping", description="測試Bot回應速度")
# async def ping(ctx: app_commands.AppCommandContext):
#     await ctx.respond("Pong!")


@bot.tree.command(name="ping", description="測試Bot回應速度")
async def ping(interaction: discord.Interaction):
    """
    This text will be shown in the help command
    """
    # Get the latency of the bot
    latency = bot.latency  # Included in the Discord.py library
    # Send it to the user
    await interaction.response.send_message(latency)


@bot.tree.command(name="get-server-info", description="查詢伺服器資訊")
async def get_server_info(interaction: discord.Interaction):

    await interaction.response.defer()

    url = f"{REST_API}/v1/api/info"
    # payload = {}
    headers = {
        "Accept": "application/json",
        "Authorization": "Basic YWRtaW46ZzhvbjA3OQ==",
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                status_code = response.status
                response_text = await response.text()

                embed = discord.Embed(
                    title="API 資料擷取",
                    description=f"**Status Code: `{status_code}`**",
                    url=url,
                    color=(
                        discord.Color.blue()
                        if 200 <= status_code < 300
                        else discord.Color.orange()
                    ),
                )

                if response_text:
                    file_content = io.BytesIO(response_text.encode("utf-8"))
                    is_json = "application/json" in response.headers.get(
                        "Content-Type", ""
                    )
                    filename = "response.json" if is_json else "response.txt"
                    await interaction.followup.send(
                        embed=embed, file=discord.File(file_content, filename=filename)
                    )
                else:
                    embed.add_field(name="Response Body", value="`No content`")
                    await interaction.followup.send(embed=embed)

    except Exception as e:
        await ctx.followup.send(
            f"❌ **請求過程中發生嚴重錯誤**：\n`{type(e).__name__}`: `{e}`"
        )


bot.run(TOKEN)
