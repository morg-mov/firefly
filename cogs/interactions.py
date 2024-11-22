from discord.ext import commands
from discord import SlashCommandOptionType as SlashCmdType
from discord import option
import discord
from nekosbest import Client as NekoAPIClient
from tools.interactions import create_interaction_embed

prompts_dict = {
            "baka": ("Called themself a baka!", "You should be a little nicer to yourself...", "Called {target_name} a baka!", None),
            "bite": ("Bit themself...?", None, "Bit {target_name}!", None),
            "cuddle": ("Cuddled... themselves.", "...are you okay? :(", "Cuddled with {target_name}!", None),
            "handhold": ("Held their own hand...", "How unfortunate...", "Held {target_name}'s hand...", None),
            "hug": ("Hugged... Themself?", None, "Hugged {target_name}!", None),
            "kick": ("Kicked themselves!", "Why'd you do that????", "Kicked {target_name}!", None),
            "kiss": ("Kissed themselves!", "Now that's self-love!", "Kissed {target_name}!", None),
            "pat": ("Gave... themself pats?", None, "Patted {target_name}!", None),
            "poke": ("Poked themselves!", "Who's attention are you trying to get exactly?", "Poked {target_name}!", None),
            "punch": ("Punched themselves!", "Why???", "Punched {target_name}!", None),
            "shoot": ("Shot... themselves...", "That's... not good.", "Shot {target_name}!", None),
            "slap": ("Slapped themselves!", "Why are you doing that to yourself??", "Slapped {target_name}!", None),
            "stare": ("Stared at... themselves?", "You must be really bored.", "Stared at {target_name}.", "o_o"),
            "tickle": ("Tickled... themselves?", "I don't think that's...even possible.", "Tickled {target_name}!", None),
            "wave": ("Waved at themselves.", "Hello darkness, my old friend...", "Waved at {target_name}!", None),
            "wink": ("Winked at... themselves?", "Are you trying to seduce yourself?", "Winked at {target name}!", ";)"),
            "yeet": ("Yeeted... themselves?", "How do you even manage that?", "Yeeted {target_name}!", None)
    }

def setup(bot: discord.Bot):
    """Define Command Groups"""
    bot.add_cog(Interactions(bot))

class Interactions(commands.Cog):

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.api_client = NekoAPIClient()

    @commands.slash_command(name="interact", description="Interact with another user!")
    @option(name="interact_type", choices=prompts_dict.keys())
    async def interactcmd(
        self,
        ctx: discord.ApplicationContext,
        interact_type: str,
        target: SlashCmdType.user
    ):
        prompts: tuple = prompts_dict.get(interact_type, None)
        if prompts is None:
            await ctx.respond("Command not found. How did you manage that?", ephemeral=True)
            return None
        
        await ctx.defer()

        image_data = await self.api_client.get_image(interact_type, 1)

        if target == ctx.author:
            await ctx.respond(embed=create_interaction_embed(image_data, ctx.author, prompts[0], prompts[1]))
            return None
        
        await ctx.respond(embed=create_interaction_embed(image_data, ctx.author, prompts[2].format(target_name=target.name), prompts[3]), content=target.mention)
