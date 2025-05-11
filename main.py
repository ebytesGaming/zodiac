import discord
import asyncio

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        self.loop.create_task(self.status_cycle())

    async def status_cycle(self):
        while True:
            await self.change_presence(activity=discord.Game(name="on ZodiacSMP"), status=discord.Status.dnd)
            await asyncio.sleep(59)
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="AstroBytes"), status=discord.Status.dnd)
            await asyncio.sleep(59)

intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run('MTMzNDYxMDg3MjgzNTc3MjU2Nw.GobfHC.yEczHfvxm8nvI9oJ5asl2nsFw2mtA7JQ4ia7fs')
