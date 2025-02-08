import requests
from discord.utils import get
import asyncio
import discord
from discord import ui
from discord import app_commands


TEST_GUILD = 1232373709767970846

def load_names(filename: str):
    """Loads names from a file into a dictionary."""
    name_map = {}
    with open(filename, "r") as file:
        for line in file:
            if "=" in line:  # Ensure valid format
                key, value = line.strip().split("=")  # Split into key-value pair
                name_map[key] = value
    return name_map

def find_name(name: str, nameMap: dict):
    return nameMap.get(name)

def nameToUUID(username):
    url = f'https://api.mojang.com/users/profiles/minecraft/{username}'
    r = requests.get(url)

    if r.status_code == 200:  # If the response is valid
        data = r.json()
        return data.get('id')
    else:
        return False  # If the username doesn't exist, return False

class MyClient(discord.Client):
    def __init__(self) -> None:
        # Just default intents and a `discord.Client` instance
        # We don't need a `commands.Bot` instance because we are not
        # creating text-based commands.
        intents = discord.Intents.all()
        super().__init__(intents=intents)

        # We need an `discord.app_commands.CommandTree` instance
        # to register application commands (slash commands in this case)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self) -> None:
        # Sync the application command with Discord.
        await self.tree.sync(guild=discord.Object(id=TEST_GUILD))


class Form(discord.ui.Modal, title="Minecraft IGN"):
    answer = ui.TextInput(
        label="Please Input Your IGN",
        style=discord.TextStyle.short,
        placeholder="Technoblade",
        required=True,
        min_length=3,
        max_length=16
    )

    async def on_submit(self, interaction: discord.Interaction):
        if nameToUUID(self.answer.value) != False:
            filename = "names.txt"
            nameMap = load_names(filename)

            IGN = find_name(interaction.user.name, nameMap)
            if IGN == None:
                with open("names.txt", "a") as f:
                    f.write(f"{interaction.user.name}={self.answer.value}\n")

                await interaction.response.send_message("Submission Entered", ephemeral=True)
            else:
                with open(filename, "r", encoding="utf-8") as file:
                    content = file.read()
                remove = interaction.user.name + "=" + IGN
                content = content.replace(remove, interaction.user.name + "=" + self.answer.value)
                with open(filename, "w", encoding="utf-8") as file:  # Write changes back
                    file.write(content)
                await interaction.response.send_message("Submission Entered", ephemeral=True)
        else:
            await interaction.response.send_message("Submission Disregarded, Not Valid Username", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

def levelToPrefixColor(level):        # Just returns the prefix color
    level = int(level)
    if level < 40:
        return "#9D9D97"
    if level > 40 and level < 80:
        return "#F9FFFE"
    if level > 80 and level < 120:
        return "#FED83D"
    if level > 120 and level < 160:
        return "#80C71F"
    if level > 160 and level < 200:
        return "#5E7C16"
    if level > 200 and level < 240:
        return "#3AB3DA"
    if level > 240 and level < 280:
        return "#169C9C"
    if level > 280 and level < 320:
        return "#3C44AA"
    if level >320 and level < 360:
        return "#F38BAA"
    if level > 360 and level < 400:
        return  "#8932B8"
    if level >400 and level < 440:
        return  "#F9801D"
    if level > 440:
        return "#B02E26"

def getActiveProfile(NAME, API_KEY):
    url = f"https://api.hypixel.net/v2/skyblock/profiles?uuid={NAME}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if not data.get("success", False):
        raise Exception("Failed to fetch data. Check API key and UUID.")
    
    profiles = data.get("profiles", [])
    if not profiles:
        return None  # No profiles found
    
    for profile in profiles:
        if profile.get("selected", False):
            return profile
    return None

def getSkyblockLevel(username):
    API_KEY = "SKYBLOCK_API_KEY"

    UUID = nameToUUID(username)
    profile = getActiveProfile(NAME=UUID, API_KEY=API_KEY)
    profile = profile["members"]
    profile = profile[UUID]
    profile = profile["leveling"]
    exp = profile["experience"]
    level = round(exp / 100)
    return level


client = MyClient()

@client.tree.command(guild=discord.Object(id=TEST_GUILD), description="Input your IGN so you can get a appropriate level role")
async def form(interaction: discord.Interaction):
    await interaction.response.send_modal(Form())

@client.tree.command(guild=discord.Object(id=TEST_GUILD), description="Updates everyone's level roles!")
async def update(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.defer(ephemeral=True)
    tasks = []  # to hold the member role update tasks
    
    filename = "names.txt"
    nameMap = load_names(filename)

    for member in guild.members:
        IGN = find_name(member.name, nameMap)
        if IGN is not None:
            # Find any existing role that starts with "LVL:"
            old_role = next((role for role in member.roles if role.name.startswith("LVL:")), None)
            
            # If an old role is found, remove it
            if old_role:
                tasks.append(member.remove_roles(old_role))
            
            # Get the new role based on the Skyblock level
            skyblockLevel = getSkyblockLevel(IGN)
            checkRole = discord.utils.get(guild.roles, name=f"LVL: {skyblockLevel}")

            if checkRole is None:
                hex = levelToPrefixColor(skyblockLevel)
                colour = discord.Colour.from_rgb(*(int(hex[i:i+2], 16) for i in (1, 3, 5)))
                role = await guild.create_role(name=f"LVL: {skyblockLevel}", colour=colour)
                tasks.append(member.add_roles(role))
            else:
                tasks.append(member.add_roles(checkRole))

    # Execute all tasks concurrently
    await asyncio.gather(*tasks)

    # Send the follow-up message after the loop
    await interaction.followup.send("Finished Updating All Roles", ephemeral=True)





client.run("TOKEN")