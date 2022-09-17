from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from cogs.bridge.main import fetch_webhook_guild
import discord
import os

load_dotenv()


class utils(commands.Cog):
    def __init__(self,bot:commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name="info",description="instance info")
    async def info(self,interaction:discord.Interaction):
        whg = await fetch_webhook_guild(interaction.guild)
        em = discord.Embed(title="Fedicord",description=f"instance: {os.getenv('INSTANCE_NAME')}")
        em.add_field(name="channel",value=f"<#{whg[1]}>")
        em.add_field(name="guilds",value=len(self.bot.guilds))
        em.add_field(name="ping",value=f"{round(self.bot.latency * 1000)}ms")
        await interaction.response.send_message(embed=em)

async def setup(bot):
    await bot.add_cog(utils(bot))