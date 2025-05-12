import discord
from discord.ext import commands
from discord import app_commands 
import asyncio
import io
from collections import Counter
import os
# --- dotenv for loading environment variables ---


class Client(commands.Bot):
    async def on_ready(self ):
         print(f'Logged on as {self.user}!')
         self.loop.create_task(self.cycle_status())

    async def on_message(self, message):
     if message.author == self.user:
        return

     if message.content.startswith('-id'):
        await message.reply(f'**{message.author}** your ID is `{message.author.id}`')
     
     if message.content.startswith('-staff'):
         embed = discord.Embed(
             description="<:whitedot:1371179894448328834> *Apply for staff [here](https://www.youtube.com/@not_astrobytes)*",
             color=0x2F3136
         )
         await message.channel.send(embed=embed)
    
    async def on_member_join(self, member):
        channel = self.get_channel(1360521553485500497)
        if channel:
            await channel.send(f"Welcome to the server, {member.mention}!")
        role = member.guild.get_role(1360476502667296910)
        if role:
            await member.add_roles(role)

    async def cycle_status(self):
        await self.wait_until_ready()
        while not self.is_closed():
            await self.change_presence(
                activity=discord.Game(name="on ZodiacSMP"),
                status=discord.Status.invisible
            )
            await asyncio.sleep(59)
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name="AstroBytes Code"),
                status=discord.Status.dnd
            )
            await asyncio.sleep(30)

    async def setup_hook(self):
        await self.tree.sync()

 
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = Client(command_prefix="!", intents=intents)

@client.tree.command(name="server-info", description="Check the ZodiacSMP private server information!")
async def server_info(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.mcstatus.io/v2/status/java/play.boomsmp.net") as resp:
                data = await resp.json()
        
        online = data['players']['online']
        max_players = data['players']['max']
        ip = data['host']
        player_list = ', '.join(data['players']['list']) if data['players'].get('list') else "No players online"

        embed = discord.Embed(title="ZodiacSMP Server Info", color=0x2F3136)
        embed.add_field(name="IP", value=ip, inline=False)
        embed.add_field(name="Players Online", value=f"{online}/{max_players}", inline=False)
        embed.add_field(name="Online Players", value=player_list, inline=False)
        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")

# ---- Ticket System ----
from discord.ui import View, Button

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="General Support", style=discord.ButtonStyle.gray, custom_id="general_support")
    async def general_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "general")

    @discord.ui.button(label="Paid Partnership Support", style=discord.ButtonStyle.gray, custom_id="partnership_support")
    async def partnership_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "partnership")

    async def create_ticket(self, interaction, category_name):
        guild = interaction.guild
        existing = discord.utils.get(guild.text_channels, name=f"{category_name}-ticket-{interaction.user.name}")
        if existing:
            return await interaction.response.send_message("🌌 You’ve already opened a ticket!", ephemeral=True)

        category = discord.utils.get(guild.categories, name="Tickets")
        if category is None:
            category = await guild.create_category("Tickets")

        support_role = guild.get_role(1360980581546065981)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True),
        }
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"{category_name}-ticket-{interaction.user.name}",
            overwrites=overwrites,
            category=category
        )

        if category_name == "general":
            embed = discord.Embed(
                title="🌌 ZodiacSMP General Support",
                description="Let us know what you need help with — the more details, the better.\nHang tight and we’ll be with you shortly. Thanks for your patience and for being part of ZodiacSMP! ♊",
                color=0x9B59B6
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1245480043451383840/1245878602340368536/image.png?ex=6813581e&is=6812069e&hm=15408f1acd7e46ab000475a44bc6e4df4358f70209b38e9ff7743f517199cdcc&=&format=webp&quality=lossless&width=2844&height=22")
            await channel.send(content=f"{interaction.user.mention}", embed=embed, view=TicketManagementView())
        else:
            await channel.send(content=f"{interaction.user.mention}, welcome to your **{category_name.replace('_', ' ')}** ticket! A staff member will be with you shortly.", view=TicketManagementView())

        await interaction.response.send_message(f"Your ticket has been created: {channel.mention}", ephemeral=True)


class TicketManagementView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.blurple, custom_id="claim_ticket")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role = interaction.guild.get_role(1360980581546065981)
        if staff_role not in interaction.user.roles:
            return await interaction.response.send_message("Only staff can claim tickets.", ephemeral=True)
        await interaction.channel.send(f"{interaction.user.mention} has claimed this ticket.")
        await interaction.response.defer()

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        log_channel = interaction.guild.get_channel(1296644287294996540)
        messages = [msg async for msg in interaction.channel.history(limit=None, oldest_first=True)]

        # Count messages per user
        user_counts = Counter(msg.author.display_name for msg in messages)

        # Build formatted message list
        formatted_messages = "\n".join(
            f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {msg.author}: {msg.content}"
            for msg in messages
        ) or "No messages found."

        # Create .txt file
        transcript_file = discord.File(
            fp=io.StringIO(formatted_messages),
            filename=f"{interaction.channel.name}_transcript.txt"
        )

        # Construct embed
        embed = discord.Embed(
            title=f"TRANSCRIPT: {interaction.channel.category.name if interaction.channel.category else 'Ticket'}",
            description=(
                f"**Ticket Name:**\n{interaction.channel.name}\n"
                f"**Opened By:**\n<@{messages[0].author.id}>\n"
                f"**Deleted By:**\n{interaction.user.mention}\n"
                f"**Users in Ticket:**\n" +
                "\n".join(f"{name} - {count} Messages" for name, count in user_counts.items())
            ),
            color=discord.Color.dark_purple()
        )

        # Send transcript
        if log_channel:
            await log_channel.send(embed=embed, file=transcript_file)

        await interaction.response.send_message("Ticket closing in 5 seconds...", ephemeral=False)
        await asyncio.sleep(5)
        await interaction.channel.delete()


@client.tree.command(name="ticket", description="Open a support ticket interface.")
async def ticket_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="`🌌` Welcome to ZodiacSMP Support!",
        description="Need help? You’re in the right place! Please read the rules below before opening a ticket to ensure a smooth support experience.",
        color=0x2F3136
    )
    embed.add_field(name="📜 Rule 1", value="Be respectful and patient with the staff. Rude behavior won't be tolerated.", inline=True)
    embed.add_field(name="📜 Rule 2", value="Only open a ticket if you have a real issue or question. Don’t spam tickets.", inline=True)
    embed.add_field(name="📜 Rule 3", value="Do not ping staff unnecessarily — we’ll get to you as soon as we can!", inline=True)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1245480043451383840/1245878602340368536/image.png?ex=6821d89e&is=6820871e&hm=6246f3084cb39add90ab8a9ebd88972958cd857554fa6fa2d5f36b6fa48acddb")
    await interaction.response.send_message("Embed sent!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=TicketView())
 
import aiohttp
import logging
logging.basicConfig(level=logging.INFO)

@client.tree.command(name="add", description="Add a member to this ticket")
@app_commands.describe(user="User to add to the ticket")
async def add_to_ticket(interaction: discord.Interaction, user: discord.Member):
    if not any(interaction.channel.name.startswith(prefix) for prefix in ["general-ticket-", "partnership-ticket-"]):
        return await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
    await interaction.channel.set_permissions(user, view_channel=True, send_messages=True, attach_files=True, read_message_history=True)
    await interaction.response.send_message(f"{user.mention} has been added to the ticket.")

@client.tree.command(name="close", description="Close this ticket")
async def close_ticket(interaction: discord.Interaction):
    if not any(interaction.channel.name.startswith(prefix) for prefix in ["general-ticket-", "partnership-ticket-"]):
        return await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
    await interaction.response.send_message("Ticket closing in 5 seconds...")
    await asyncio.sleep(5)
    await interaction.channel.delete()

async def main():
    async with client:
        await client.start('DISCORD_TOKEN')

asyncio.run(main())
