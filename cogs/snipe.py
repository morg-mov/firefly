from discord.ext import commands, tasks
import discord
from datetime import datetime
from typing import List

# Time for message to sit in cache before being deleted
msg_time_limit = 60
# Attachment size limit in megabytes, this needs to be set in accordance to your system and download speed,
# since the bot needs to cache the attachment in between the window where the message is deleted, and
# Discord disabling downloads for the attachment.
attch_size_limit = 25

class Snipe(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.deleted_msg: discord.Message = None
        self.deleted_msg_time: datetime.datetime = None
        self.deleted_attachments: List[discord.File] = None
        self.file_omitted: bool = False

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        self.deleted_msg = message
        self.deleted_msg_time = datetime.now()
        if self.deleted_msg.attachments is not None:

            for attachment in self.deleted_msg.attachments:
                # Check if filesize is greater than the attachment size limit
                if attachment.size > (attch_size_limit*1000000):
                    self.file_omitted = True
                    continue
                
                # Set deleted attachments back to list so that no errors happen when running snipe
                if self.deleted_attachments is None:
                    self.deleted_attachments = []

                file = await attachment.to_file()
                self.deleted_attachments.append(file)

    @tasks.loop(seconds=1)
    async def check_msg_time(self):
        if (self.deleted_msg_time - datetime.now()).total_seconds() > msg_time_limit:
            await self.clear_snipe_cache()

    async def clear_snipe_cache(self):
            self.deleted_msg = None
            self.deleted_msg_time = None
            self.deleted_attachments = None
            self.file_omitted = False

    @commands.slash_command(description="\"Undelete\" the last deleted message (within the last minute)")
    async def snipe(self, ctx: discord.ApplicationContext):
        # Stop bot from giving up, letting down, running around, and deserting you
        await ctx.defer()

        if self.deleted_msg is None:
            await ctx.respond(f"No messages found. (Message must've been deleted within the last {msg_time_limit} seconds.)")
            return
        
        embed = discord.Embed(
            color=discord.Color.red(),
            description=str(self.deleted_msg.content),
            timestamp=self.deleted_msg.created_at,
        )
        embed.set_author(name=self.deleted_msg.author.name, icon_url=self.deleted_msg.author.avatar.url, url=self.deleted_msg.author.jump_url)
       
        # Notifies user when attachment was omitted due to file limit.
        if self.file_omitted:
            embed.set_footer(text=f"One or more of the attached files was over {str(attch_size_limit)}MB, and was omitted.")
        
        if self.deleted_attachments is None:
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(embed=embed, files=self.deleted_attachments)
        
        await self.clear_snipe_cache()

def setup(bot: discord.Bot):
    bot.add_cog(Snipe(bot))