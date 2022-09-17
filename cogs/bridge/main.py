from typing import Optional, Union
import discord
import aiosqlite
from discord import app_commands
from discord.ext import commands

def check_if_it_is_me(interaction: discord.Interaction) -> bool:
        return interaction.user.id == 891747020149235812

async def make_webhook(channel:discord.TextChannel):
    async with aiosqlite.connect("db/main.sqlite") as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT * FROM webhooks WHERE server = ?", (channel.guild.id,))
                    result = await cur.fetchone()
                    if result:
                        return 0
                    else:
                        hook = await channel.create_webhook(name="fedihook")
                        hook
                        await cur.execute("INSERT INTO webhooks(server, id, url) VALUES (?,?,?)", (channel.guild.id,channel.id,hook.id))
                        await conn.commit()
                        return 1

async def delete_webhook(channel:discord.TextChannel):
    async with aiosqlite.connect("db/main.sqlite") as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT * FROM webhooks WHERE server = ?", (channel.guild.id,))
                    result = await cur.fetchone()
                    if result:
                        wh = await channel.webhooks()
                        for weh in wh:
                            if weh.id == result[2]:
                               await weh.delete()
                        await cur.execute("DELETE FROM webhooks WHERE server = ?", (channel.guild.id,))
                        await conn.commit()
                        return 0
                    else:
                        return 1

async def fetch_webhook(channel:discord.TextChannel):
    async with aiosqlite.connect("db/main.sqlite") as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT * FROM webhooks WHERE id = ?", (channel.id,))
                    result = await cur.fetchone()
                    if result:
                        return result
                    else:
                        return 1

async def fetch_blacklist(user:discord.Member):
    async with aiosqlite.connect("db/main.sqlite") as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT * FROM blacklist WHERE user_id = ?", (user.id,))
                    result = await cur.fetchone()
                    if result:
                        return 0
                    else:
                        return 1

async def fetch_webhook_guild(guild:discord.Guild):
    async with aiosqlite.connect("db/main.sqlite") as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT * FROM webhooks WHERE server = ?", (guild.id,))
                    result = await cur.fetchone()
                    if result:
                        return result
                    else:
                        return False


class bridge(commands.Cog):
    def __init__(self,bot:commands.Bot) -> None:
        self.bot = bot
        super().__init__()
    
        @bot.event
        async def on_message(msg:discord.Message):
            if await fetch_blacklist(msg.author) == 1:
                shook = await fetch_webhook(msg.channel)
                if not shook == 1:
                    async for server in bot.fetch_guilds():
                        if not server.id == msg.guild.id and not msg.webhook_id:
                            hook = await fetch_webhook_guild(server)
                            if not hook == False:
                                channel = await bot.fetch_webhook(hook[2])
                                files = []
                                for attachment in msg.attachments:
                                    file = await attachment.to_file(filename=attachment.filename)
                                    files.append(file)

                                await channel.send(msg.content,username=f"{msg.author.name}@{msg.guild.name}",avatar_url=msg.author.avatar.url,files=files,embeds=msg.embeds)

    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="register")
    async def register(self,interaction:discord.Interaction):
        mk = await make_webhook(interaction.channel)
        if mk == 0:
            await interaction.response.send_message("Only one channel per guild can be registered")
        elif mk == 1:
            await interaction.response.send_message("This channel has just been registered!")

        
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="unregister")
    async def unregister(self,interaction:discord.Interaction):
        mk = await delete_webhook(interaction.channel)
        if mk == 0:
            await interaction.response.send_message("Webhook unregistered")
        elif mk == 1:
            await interaction.response.send_message("No channel was found")

    @app_commands.check(check_if_it_is_me)
    @app_commands.command(name="blacklist", description="Globally ban a user from using this Fedicord instance")
    async def blacklist(self, inter: discord.Interaction, user: Union[discord.Member, discord.User], reason: Optional[str] = "No reason provided") -> None:
        async with aiosqlite.connect("db/main.sqlite") as conn:
            async with conn.cursor() as cur:
                await cur.execute("INSERT INTO blacklist(user_id, reason) VALUES (?, ?)", (user.id, reason))
                await conn.commit()
        await inter.response.send_message(f"Blacklisted ID {user.id}", ephemeral=True)



async def setup(bot):
    await bot.add_cog(bridge(bot))