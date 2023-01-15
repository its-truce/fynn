import discord
from discord.ext import commands
from discord import app_commands
from sqlitedict import SqliteDict

token = "YOUR TOKEN HERE"

intents = discord.Intents.default()
intents.message_content= True
intents.members = True
activity = discord.Game(name="Slash Commands")

bot = commands.Bot(command_prefix=".", intents=intents, activity=activity)

@bot.command()
async def sync(ctx):
    await bot.tree.sync()

@bot.tree.command(description="Sample text.")
async def lorem(interaction: discord.Interaction):
    await interaction.response.send_message("Lorem ipsum dolor sit amet.", ephemeral=False)

@bot.tree.command(description="Says what you say.")
@app_commands.describe(message = "Your message")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(f"{message}", ephemeral=False)

@bot.tree.command(description="Adds two numbers.")
@app_commands.describe(first = "The first number", second = "The second number")
async def add(interaction: discord.Interaction, first: float, second: float):   
    await interaction.response.send_message(f"{first} + {second} is equal to {first + second}.", ephemeral=False)

# Reaction Logging
rec: discord.TextChannel = None
rec_logs = SqliteDict("./rec_logs.sqlite")

@bot.event
async def on_reaction_add(reaction, member):
    global rec
    ms = reaction.message.jump_url
    cs = reaction.message.channel
    us = f"{member.name}#{member.discriminator}"
    rs = reaction.emoji
    es = reaction.message.author
    emr = discord.Embed(color=0x2F3136, title="Reaction Added!", description=f"**Message:** [Click here!]({ms})\n**member:** {us}\n**Author:** {es}\n**Emote**: {rs}\n**Channel:** {cs.mention}")
    guild_id = reaction.message.guild.id
    if guild_id in rec_logs:
        channel_id = rec_logs[guild_id]
        rec = bot.get_channel(channel_id)
        await rec.send(embed = emr)

@bot.tree.command(description="Sets up reaction logging.")
@app_commands.describe(channel = "The channel to log to.", on = "Turn reaction logging on or off.")
@app_commands.checks.has_permissions(manage_messages=True)
async def reaction_log(interaction: discord.Interaction, on: bool, channel: discord.TextChannel):
    if on:
        await interaction.response.send_message(f"Reaction detection will now be reported in {channel.mention}.", ephemeral=False)
        guild_id = interaction.guild.id
        rec_logs[guild_id] = channel.id
        rec_logs.commit()
    elif not on:
        guild_id = interaction.guild.id
        if guild_id not in rec_logs:
            await interaction.response.send_message(f"Reaction logging has not been setup!")
        else:
            del rec_logs[guild_id]
            await interaction.response.send_message(f"Reaction logging has been stopped for this guild.")
            rec_logs.commit()

# Deletion Logging
delc: discord.TextChannel = None
del_logs = SqliteDict("./del_logs.sqlite")

@bot.event
async def on_message_delete(message):
    global delc
    ms = message.content
    cs = message.channel
    us = message.author
    emd = discord.Embed(color=0x2F3136, title="Message Deleted!", description=f"**Message:** {ms}\n**Author:** {us}\n**Channel:** {cs.mention}")
    guild_id = message.guild.id
    if guild_id in del_logs:
        channel_id = del_logs[guild_id]
        delc = bot.get_channel(channel_id)
        await delc.send(embed = emd)

@bot.tree.command(description="Set up message deletion logging.")
@app_commands.describe(channel = "The channel to log to.", on = "Turn deletion logging on or off.")
@app_commands.checks.has_permissions(manage_messages=True)
async def deletion_log(interaction: discord.Interaction, on: bool, channel: discord.TextChannel):
    if on:
        await interaction.response.send_message(f"Deletion logging will now be reported in {channel.mention}.", ephemeral=False)
        guild_id = interaction.guild.id
        del_logs[guild_id] = channel.id
        del_logs.commit()
    elif not on:
        guild_id = interaction.guild.id
        if guild_id not in del_logs:
            await interaction.response.send_message(f"Deletion logging has not been setup!")
        else:
            del del_logs[guild_id]
            await interaction.response.send_message(f"Deletion logging has been stopped for this guild.")
            del_logs.commit()

# Edit Logging
edic: discord.TextChannel = None
edit_logs = SqliteDict("./edit_logs.sqlite")

@bot.event
async def on_message_edit(before, after):
    global edic
    ms = before.content
    es = after.content
    cs = before.channel
    us = before.author
    js = after.jump_url
    eme = discord.Embed(color=0x2F3136, title="Message Edited!", description=f"**Original:** {ms}\n**Edited:** {es}\n**Author:** {us}\n**Message:** [Click here!]({js})\n**Channel:** {cs.mention}")
    guild_id = before.guild.id
    if guild_id in edit_logs:
        channel_id = edit_logs[guild_id]
        edic = bot.get_channel(channel_id)
        await edic.send(embed = eme)

@bot.tree.command(description="Set up message edit logging.")
@app_commands.describe(channel = "The channel to log to.", on = "Turn edit logging on or off.")
@app_commands.checks.has_permissions(manage_messages=True)
async def edit_log(interaction: discord.Interaction, on: bool, channel: discord.TextChannel):
    if on:
        await interaction.response.send_message(f"Edited message logging will now be reported in {channel.mention}.", ephemeral=False)
        guild_id = interaction.guild.id
        edit_logs[guild_id] = channel.id
        edit_logs.commit()
    elif not on:
        guild_id = interaction.guild.id
        if guild_id not in edit_logs:
            await interaction.response.send_message(f"Edited message logging has not been setup!")
        else:
            del edit_logs[guild_id]
            await interaction.response.send_message(f"Edited message logging has been stopped for this guild.")
            edit_logs.commit()

# Reporting Setup
report_logs = SqliteDict("./report_logs.sqlite")

@bot.tree.command(description="Set up message reporting.")
@app_commands.describe(channel = "The channel to report to.", on = "Turn reporting on or off.")
@app_commands.checks.has_permissions(manage_messages=True)
async def reporting(interaction: discord.Interaction, on: bool, channel: discord.TextChannel):
    if on:
        await interaction.response.send_message(f"Reported messages will now be reported in {channel.mention}.", ephemeral=False)
        guild_id = interaction.guild.id
        report_logs[guild_id] = channel.id
        report_logs.commit()
    elif not on:
        guild_id = interaction.guild.id
        if guild_id not in report_logs:
            await interaction.response.send_message(f"Reporting has not been setup!")
        else:
            del report_logs[guild_id]
            await interaction.response.send_message(f"Reporting has been stopped for this guild.")
            report_logs.commit()

# Report Message
@bot.tree.context_menu()
@app_commands.describe(message = "The message to be reported")
async def report(interaction: discord.Interaction, message: discord.Message):
    guild_id = interaction.guild.id
    if guild_id not in report_logs:
        await interaction.response.send_message("Reporting has not been setup!", ephemeral=True)
    else:
        await interaction.response.send_message("Message has been reported.", ephemeral=True)
        em = discord.Embed(color=0x2F3136, title=f"You have been reported.", description=f"One of your messages was reported in {message.guild.name} by another user.\n\nIt has been sent to the server's staff for consideration.")
        await message.author.send(embed=em) 
        channel_id = report_logs[guild_id]
        emr = discord.Embed(color=0x2F3136, title=f"Message Reported!", description=f"**Content:** {message.content}\n**Author:** {message.author}\n**Message:** [Click here!]({message.jump_url})\n**Channel:** {message.channel.mention}")
        await bot.get_channel(channel_id).send(embed=emr)

# User Info
@bot.tree.command(description="Displays info about the member.")
@app_commands.describe(member = "The member to display info about.")
async def user_info(interaction: discord.Interaction, member: discord.Member):
    if member.bot:
        ub = f"User is a bot."
    elif not member.bot:
        ub = f"User is not a bot."
    rls = []
    for role in member.roles:
        if role.name != "@everyone":
            rls.append(role.mention)
    ur = ", ".join(rls)
    em = discord.Embed(color=0x2F3136, title=f"{member.name}'s Info", description=f"**Username:**\n{member.name}#{member.discriminator}\n\n**Bot Status:**\n{ub}\n\n**User ID:**\n{member.id}\n\n**Joined At:**\n{discord.utils.format_dt(member.joined_at)}\n\n**Account Created At:**\n{discord.utils.format_dt(member.created_at)}\n\n**Roles:**\n{ur}")
    em.set_thumbnail(url=member.display_avatar.url)
    await interaction.response.send_message(embed = em)

# Member List
@bot.tree.command(description="Sends total number of members, bots, and humans.")
async def members(interaction: discord.Interaction):
    guild = interaction.guild
    lst = guild.members
    bot = 0
    mem = 0
    for member in lst:
        if member.bot:
            bot += 1
        else:
            mem +=1
    em = discord.Embed(color=0x2F3136, title="Member Count", description=f"**Bots:** {bot}\n**Humans:** {mem}\n**Total:** {mem + bot}")
    await interaction.response.send_message(embed = em)

# Error Handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"I don't have this commmand. Use `.help` to get a list of all commands and their usage.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Your command is incomplete. Please add required arguments. Use `.help` to get a list of all commands and their usage.")
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send(f"Your argument is not a channel. Please mention a channel. Use `.help` to get a list of all commands and their usage.")
    elif isinstance(error, commands.MissingPermissions):
        perms = ", ".join(error.missing_permissions)
        await ctx.send(f"You don't have permissions to use this command! It requires `{perms}` to use.")
    elif isinstance(error, commands.BotMissingPermissions):
        perms = ", ".join(error.missing_permissions)
        await ctx.send(f"I need the `{perms}` permission to use this command.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("That member could not be found. You can try pinging them or using their ID instead.")
    else:
        await ctx.send(f"Error: {error}. Please report this to `truce#7887`.")
        raise error

bot.run(token)
