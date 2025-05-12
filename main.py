import disnake
from disnake.ext import commands

bot = commands.InteractionBot(intents=disnake.Intents.default())

@bot.event
async def on_ready():
    print("Bot is online")
    await bot.wait_until_first_connect()
    await bot.change_presence(
        status=disnake.Status.idle,
        activity=disnake.Activity(
            name="on the ZodiacSMP", 
            type=disnake.ActivityType.playing,
            start=disnake.utils.utcnow(), 
            large_image="https://cdn.discordapp.com/avatars/1334610872835772567/469e97aee389287ecdda0b4650965802.webp?size=1024&format=webp&width=1024&height=1024"
        )
    )

bot.run("MTMzNDYxMDg3MjgzNTc3MjU2Nw.G4jKLL.mN39FfRzhnA8eU8gT59_WO_Zmg82aXvQRvMCSs")
