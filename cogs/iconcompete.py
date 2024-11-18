import os
from io import BytesIO
from uuid import uuid4
from datetime import datetime
from asyncio import run as asyncrun
from asyncio import sleep
import discord
from discord import SlashCommandOptionType as SlashCmdType
from discord.ext import commands
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from boto3 import client as s3_client
from botocore.client import Config as S3Config
from dbmodels.iconcompete import Submission, Upvote, Base
from tools.iconcompete import create_embed_from_model
from tools.databases import initialize_database, create_database_info

acceptable_fileends = (".jpg", ".jpeg", ".png", ".gif")


def setup(bot: discord.Bot):
    """Define Command Groups"""
    bot.add_cog(IconContest(bot))


class IconContest(commands.Cog):
    iconcontest = discord.SlashCommandGroup(
        "iconcontest", "Commands relating to Icon Contest system."
    )
    admincommands = iconcontest.create_subgroup(
        "admin", "Commands for administering icon contests."
    )

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.db_uri, self.db_dirpath, self.db_filepath = create_database_info("iconcompete.db")
        self.db_engine = create_async_engine(self.db_uri)
        self.r2_client = s3_client(
            "s3",
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            endpoint_url=os.getenv("S3_ENDPOINT"),
            config=S3Config(signature_version="s3v4"),
        )
        self.r2_bucket = os.getenv("S3_BUCKET_NAME")
        self.r2_url = os.getenv("S3_PUBLIC_URL")

        if not os.path.isfile(self.db_filepath):
            asyncrun(initialize_database(self.db_uri, self.db_dirpath, Base))

    @iconcontest.command(description="Submit an image/name combo for the icon contest!")
    async def submit(
        self,
        ctx: discord.ApplicationContext,
        svr_image: SlashCmdType.attachment,
        svr_name: str,
    ):
        # Check if file ending is foreign
        if not svr_image.filename.endswith(acceptable_fileends):
            await ctx.respond(
                "Unsupported filetype. Please submit a .PNG, .JP(E)G, or .GIF file.",
                ephemeral=True,
            )
            return None

        # Check if server name is over Discord's maximum
        if len(svr_name) > 100:
            await ctx.respond(
                "Server name too long. Must be 100 characters or less.", ephemeral=True
            )
            return None

        #

        # Defer to acknowledge command receipt
        await ctx.defer()

        # Create database engine/session
        localsession = sessionmaker(
            self.db_engine, expire_on_commit=False, class_=AsyncSession
        )

        # Check if submission has already been made in the server the command has been ran from.
        async with localsession() as session:
            stmt = select(Submission).where(
                Submission.user_id == ctx.author.id, Submission.svr_id == ctx.guild_id
            )
            result = await session.execute(stmt)
            data = result.scalar_one_or_none()
            if data is not None:
                await ctx.respond(
                    embed=create_embed_from_model(
                        data, "You've already made a submission!", discord.Color.blue()
                    )
                )
                return None

        # Gather metadata
        submissionid = str(uuid4())
        userid = ctx.author.id
        serverid = ctx.guild_id
        timestamp = datetime.now().replace(microsecond=0)
        file_extension = svr_image.filename.split(".")
        file_extension = file_extension[len(file_extension) - 1]
        file_name = f"{submissionid}.{file_extension}"
        file = BytesIO(await svr_image.read())

        # Acknowledge receipt of submission
        await ctx.respond("Submission received, processing...")

        # Upload image to R2 Bucket for storage
        try:
            self.r2_client.upload_fileobj(file, self.r2_bucket, file_name)
        except Exception as e:  # i know this should be specific exceptions. blame amazon who made boto3 with 500 million exceptions with no base exception.
            ctx.edit(
                f"An error has occurred during upload. Send this to someone who can deal with it.\n\n{e}"
            )

        # Construct and commit database entry
        async with localsession() as session:
            async with session.begin():
                submission = Submission(
                    id=submissionid,
                    svr_id=serverid,
                    user_id=userid,
                    timestamp=timestamp,
                    name=svr_name,
                    filename=file_name,
                )
                session.add(submission)
                await session.commit()

        await sleep(1)
        await ctx.edit(
            embed=create_embed_from_model(
                submission, "Submitted!", discord.Color.green()
            ),
            content=None,
        )

