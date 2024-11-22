from discord.ext import commands, tasks
import discord
from datetime import datetime
from typing import List

class Snipe(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.deleted_msg: discord.Message = None
        self.deleted_msg_time: datetime.datetime = None

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.deleted_msg = message
        self.deleted_msg_time = datetime.now()

    
    @tasks.loop(seconds=1)
    async def clear_snipe_cache(self):
        # Check if deleted message is older than 60 seconds, delete if so.
        if (self.deleted_msg_time - datetime.now()).total_seconds() > 60:
            self.deleted_msg = None
            self.deleted_msg_time = None

    @commands.slash_command(description="\"Undelete\" the last deleted message (within the last minute)")
    async def snipe(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        if self.deleted_msg is not None:
            embed = discord.Embed(
                color=discord.Color.red(),
                description=str(self.deleted_msg.content),
                timestamp=self.deleted_msg.created_at,
            )
            embed.set_author(name=self.deleted_msg.author.name, icon_url=self.deleted_msg.author.avatar.url, url=self.deleted_msg.author.jump_url)
            
            await ctx.respond(embed=embed)

def setup(bot: discord.Bot):
    bot.add_cog(Snipe(bot))