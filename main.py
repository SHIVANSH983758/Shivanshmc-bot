import discord
from discord.ext import commands, tasks
import os
import asyncio
from playwright.sync_api import sync_playwright

TOKEN = os.getenv("DISCORD_TOKEN")
ATERNO_USER = os.getenv("ATERNO_USER")
ATERNO_PASS = os.getenv("ATERNO_PASS")
SERVER_ID = os.getenv("SERVER_ID")
SERVER_NAME = os.getenv("SERVER_NAME")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is logged in as {bot.user.name}")
    check_status.start()

@bot.command()
async def start(ctx):
    await ctx.send("🟡 Starting server...")
    async with ctx.typing():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://aternos.org/go/")
            page.click("text=Log in")
            page.fill("input[name='user']", ATERNO_USER)
            page.fill("input[name='password']", ATERNO_PASS)
            page.click("button[type='submit']")
            page.wait_for_timeout(5000)
            page.goto(f"https://aternos.org/server/")
            page.click("#start")
            await asyncio.sleep(10)
            browser.close()
    await ctx.send("✅ Server start command sent.")

@bot.command()
async def stop(ctx):
    await ctx.send("🔴 Stopping server...")
    async with ctx.typing():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://aternos.org/go/")
            page.click("text=Log in")
            page.fill("input[name='user']", ATERNO_USER)
            page.fill("input[name='password']", ATERNO_PASS)
            page.click("button[type='submit']")
            page.wait_for_timeout(5000)
            page.goto("https://aternos.org/server/")
            page.click("#stop")
            await asyncio.sleep(10)
            browser.close()
    await ctx.send("🛑 Server stop command sent.")

@tasks.loop(minutes=2)
async def check_status():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://aternos.org/go/")
            page.click("text=Log in")
            page.fill("input[name='user']", ATERNO_USER)
            page.fill("input[name='password']", ATERNO_PASS)
            page.click("button[type='submit']")
            page.wait_for_timeout(5000)
            page.goto("https://aternos.org/server/")
            status = page.inner_text("#statuslabel")
            tps = "20" if "Online" in status else "0"
            players = page.inner_text("#players")
            browser.close()

        channel = bot.get_channel(CHANNEL_ID)
        embed = discord.Embed(
            title="🟢 ShivanshMC Server Status",
            color=discord.Color.green() if "Online" in status else discord.Color.red()
        )
        embed.add_field(name="Status", value=status, inline=False)
        embed.add_field(name="TPS", value=tps, inline=True)
        embed.add_field(name="Players", value=players, inline=True)
        await channel.send(embed=embed)

    except Exception as e:
        print("Error checking status:", e)

bot.run(TOKEN)
