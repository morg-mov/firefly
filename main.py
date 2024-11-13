import json
import sys
import os
from datetime import datetime
import logging
import discord
from dotenv import load_dotenv

intents = discord.Intents.default()
# Place any intents you wish for this bot to have here.
# https://docs.pycord.dev/en/stable/api/data_classes.html#discord.Intents.value

bot = discord.Bot(
    intents=intents, command_prefix=None, debug_guilds=[1208608149947555970]
)
config_path = "./config.json"
logfile_path = (
    f"./logs/discord-{datetime.now().replace(microsecond=0).isoformat()}.log".replace(":", "-")
)

cog_list = ["iconcompete"]

dir_list = [
    "./databases"
]

if not os.path.isdir("./logs"):
    os.makedirs("./logs")

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
fileloghandler = logging.FileHandler(filename=logfile_path, encoding="utf-8", mode="w")
fileloghandler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
streamloghandler = logging.StreamHandler(sys.stdout)
streamloghandler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(fileloghandler)
logger.addHandler(streamloghandler)


def config_setup(path) -> dict:
    """
    Initializes configuration data

    Arguments: path (str): File path to config
    Returns: Configruation Data (dict)
    """
    while True:
        token = input("Enter your Discord Bot Token: ")
        if token:
            break
        print("No bot token provided.\n")

    logger.info("Creating config.json...")
    configdata = {"token": token, "debug_log": False}
    config_save(configdata, path)
    return configdata


def config_load(path) -> dict:
    """
    Loads configuration data file from `path`

    Arguments: path (str): File path to config
    Returns: Configuration Data (dict)
    """
    return json.load(open(path, "r", encoding="utf-8"))


def config_save(configdata, path) -> None:
    """
    Saves configuration data file to `path`

    Arguments:
    configdata (dict): Configuration data to save, path (str): File path to config

    Returns: None
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(configdata, f, indent=4)
    except OSError as e:
        logger.fatal(e)
        sys.exit(1)


def load_cogs(cogs):
    for cog in cogs:
        bot.load_extension(f"cogs.{cog}")


print(
    "\n{ WSTS Server Bot }\nVersion 1.0.0\nWritten by morg.mov\nhttps://github.com/Morg-S9 \n"
)

if not os.path.isfile(config_path):
    logger.info("No config.json found. Starting Config Setup.")
    config = config_setup(config_path)
else:
    config = config_load(config_path)

if config["debug_log"]:
    logger.info("Debug logging enabled.")
    logger.setLevel(logging.DEBUG)

for dir_ in dir_list:
    if not os.path.isdir(dir_):
        os.makedirs(dir_)


@bot.event
async def on_ready():
    logger.info("Connected as %s", bot.user)


@bot.command()
async def hello(ctx):
    await ctx.respond(f"Hello {ctx.user.name}!")


@bot.command()
async def ping(ctx):
    await ctx.respond(f"Pong! ({round(bot.latency, 2)}ms)")


if __name__ == "__main__":
    load_cogs(cog_list)
    load_dotenv()
    
    bot.run(config["token"])
