from nekosbest import Result
import discord

def create_interaction_embed(result: Result, author: discord.User | discord.Member, title: str, desc: str = None) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        color=discord.Color.nitro_pink(),
        description=desc
    )

    if result.anime_name is not None:
        embed.set_footer(text=f"Anime: {result.anime_name}")
    else:
        embed.set_footer(text=f"Artist: {result.artist_name}")

    embed.set_image(url=result.url)
    embed.set_author(name=author.name, icon_url=author.avatar.url, url=author.jump_url)

    return embed
