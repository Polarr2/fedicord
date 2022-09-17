import asyncio
import aiosqlite
from pathlib import Path
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv

class fediverse(commands.Bot):
    def __init__(self):
        super().__init__(
            "f.",
            description="Federated Discord",
            intents=discord.Intents().all(),
            allowed_mentions=discord.AllowedMentions(
                users=False, replied_user=True, roles=False, everyone=False
            ),
        )

    async def load_extensions(self):
        for extension in Path(r"cogs").glob("**/*.py"):
            extension = str(extension).replace("\\", ".")[:-3]
            await self.load_extension(extension)
            print(f"loaded extension {extension}")
    
    async def on_ready(self):
        self.db = aiosqlite.connect("db/main.sqlite")
        print(f"your fedicord instance is up and running on the bot user {self.user}!")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=f"over the fediverse"))
        await self.tree.sync()

    def run(self):
        asyncio.run(self.load_extensions())
        super().run(os.getenv("TOKEN"))
