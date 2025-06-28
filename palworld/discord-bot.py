import discord
import os
import base64
import io
import aiohttp
import traceback
from typing import Optional
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

# 載入 .env 檔案中的環境變數
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_URL = os.getenv("PALWORLD_API_BASE_URL")
SERVER_ACCOUNT = os.getenv("PALWORLD_ADMIN_ACCOUNT")
SERVER_PASSWORD = os.getenv("PALWORLD_ADMIN_PASSWORD")

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


@bot.tree.command(name="help", description="Bot求助")
async def help(interaction: discord.Interaction):
    """
    求助指令
    """
    str = """get-server: 參考 https://docs.palworldgame.com/category/rest-api 有支援的指令"""
    await interaction.response.send_message(str)


@bot.tree.command(name="ping", description="測試Bot回應速度")
async def ping(interaction: discord.Interaction):
    """
    測試Bot延遲：回傳延遲值，單位秒
    """
    # Get the latency of the bot
    latency = bot.latency  # Included in the Discord.py library
    # Send it to the user
    await interaction.response.send_message(latency)


async def get_server_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """為 fetch_data 指令的 extra_param 提供自動完成選項。"""
    # 定義可用的選項與其說明
    choices = {
        "info": "info 獲取伺服器基本資訊 (名稱、版本)",
        "players": "players 獲取目前的線上玩家列表",
        "settings": "settings 獲取重要的世界設定",
        "metrics": "metrics 獲取伺服器性能、運行指標",
    }

    # 根據使用者輸入的內容，篩選出符合的選項
    filtered_choices = []
    for value, name in choices.items():
        if current.lower() in value.lower() or current.lower() in name.lower():
            filtered_choices.append(app_commands.Choice(name=name, value=value))

    # Discord 最多只能顯示 25 個選項
    return filtered_choices[:25]


@bot.tree.command(name="get-server", description="查詢伺服器資訊")
@app_commands.autocomplete(
    opt=get_server_autocomplete
)  # 關鍵：將 autocomplete 函式綁定到參數上
@app_commands.describe(opt="選擇你想獲取的資料類型")
async def get_server(interaction: discord.Interaction, opt: Optional[str] = None):
    await interaction.response.defer()
    # 根據 extra_param 動態決定 API 的路徑

    endpoint = "info"
    if opt == "players":
        endpoint = "players"
    elif opt == "settings":
        endpoint = "settings"
    elif opt == "metrics":
        endpoint = "metrics"

    url = f"{SERVER_URL}/v1/api/{endpoint}"

    auth_string = f"{SERVER_ACCOUNT}:{SERVER_PASSWORD}"
    encoded_auth_bytes = base64.b64encode(auth_string.encode("utf-8"))
    encoded_auth_string = encoded_auth_bytes.decode("utf-8")

    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {encoded_auth_string}",
    }
    print(url)
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
                # 在後台終端機印出完整的錯誤追蹤，方便開發者除錯
        print(f"錯誤：在請求 URL '{url}' 時發生例外狀況。")
        traceback.print_exc()

        # 在 Discord 中回傳更詳細的錯誤訊息給使用者
        error_message = (
            f"❌ **請求過程中發生嚴重錯誤**\n\n"
            f"**錯誤類型:** `{type(e).__name__}`\n"
            f"**錯誤訊息:** `{e}`\n"
            f"**請求的 URL:** `{url}`"
        )
        await interaction.followup.send(error_message)



bot.run(TOKEN)
