import os
from uuid import uuid4
from datetime import datetime
import discord
from discord import SlashCommandOptionType as SlashCmdType
from discord.ext import commands
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dbmodels.iconcompete import Base, Submission, Upvote
from boto3 import client
from botocore.client import Config

acceptable_fileends = (".jpg", ".jpeg", ".png", ".gif")


def setup(bot: discord.Bot):
    """Define Command Groups"""
    bot.add_cog(IconContest(bot))


async def initialize_database(sqlalc_uri: str, filepath: str):
    if not os.path.isdir(filepath):
        os.makedirs(filepath)

    engine = create_async_engine(sqlalc_uri)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


class IconContest(commands.Cog):
    iconcontest = discord.SlashCommandGroup(
        "iconcontest", "Commands relating to Icon Contest system."
    )

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @iconcontest.command()
    async def submit(
        self, ctx: discord.ApplicationContext, image: SlashCmdType.attachment, name: str
    ):
        sqlalchemy_uri = f"sqlite+aiosqlite:///databases/{ctx.guild_id}/iconcompete.db"
        rel_filepath = f"./databases/{ctx.guild_id}/"
        filename = "iconcompete.db"

        if not image.filename.endswith(acceptable_fileends):
            await ctx.respond(
                "Unsupported filetype. Please submit a .PNG, .JP(E)G, or .GIF file.",
                ephemeral=True,
            )
            return None

        await ctx.defer()

        # Check for database existence, create if not existing
        if not os.path.isfile(rel_filepath + filename):
            await initialize_database(sqlalchemy_uri, rel_filepath)

        dbengine = create_async_engine(sqlalchemy_uri)
        localsession = sessionmaker(
            dbengine, expire_on_commit=False, class_=AsyncSession
        )

        async with localsession() as session:
            stmt = select(Submission).where(Submission.user_id == ctx.author.id)
            result = await session.execute(stmt)
            data = result.scalar_one_or_none()
            if data is not None:
                await ctx.respond("You've already made a submission!")
                return None

        # Gather metadata
        submissionid = str(uuid4())
        userid = ctx.author.id
        timestamp = datetime.now().replace(microsecond=0)
        svr_image = await image.read()

        async with localsession() as session:
            async with session.begin():
                submission = Submission(
                    sub_id=submissionid,
                    user_id=userid,
                    timestamp=timestamp,
                    svr_name=name,
                    svr_img=svr_image,
                )
                session.add(submission)
                await session.commit()

        await dbengine.dispose()

        embed = (
            discord.Embed(
                colour=discord.Color.green(), title="Submitted!", description=name
            )
            .set_image(url=image.url)
            .set_footer(
                text=f"Submission ID: {submissionid}\nSubmission Time: {timestamp}"
            )
        )
        await ctx.respond(embed=embed)
