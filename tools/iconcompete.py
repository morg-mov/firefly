import os
import discord
from dbmodels.iconcompete import Submission

def create_embed_from_model(entry: Submission, title: str, color: discord.Color) -> discord.Embed:
    image_url = f"{os.getenv('S3_PUBLIC_URL')}/{entry.filename}"
    return discord.Embed(
                colour=color,
                title=title,
                description=entry.name, 
                timestamp=entry.timestamp, 
                url=image_url
            ).set_footer(text=f"Submission ID: {entry.id}\n\nIf the image doesn't load, Click the link to view the image.").set_image(url=image_url)