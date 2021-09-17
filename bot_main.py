import bot_wow_api
import discord
import os
import re

from discord.ext import commands
from datetime import datetime
from bot_text_resources import *
from bot_config import *

import bot_music

class GuildRoles:
    ROLE_FRIEND = "Friend"
    ROLE_INITIATE = "Initiate"
    ROLE_APPLICANT = "Applicant"
    ROLE_DJ = "DJ"

bot = commands.Bot(command_prefix='!', case_insensitive=True)
bot.remove_command('help')

applicants = {}

@bot.event
async def on_member_join(member):
    await member.send(ON_MEMBER_JOIN_1)
    await member.send(ON_MEMBER_JOIN_2)
    
@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def application(ctx):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send(APPLICATION_PUBLIC)
        
    await ctx.author.send(APPLICATION)


def applicant(applicant_map, member):
    if member not in applicant_map:
        applicant_map[member] = {}
        
    return applicant_map[member]


@bot.command()
@commands.cooldown(1, 1, commands.BucketType.user)
async def armory(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        if len(ctx.message.content.strip().split(" ")) <= 1:
            await ctx.author.send(APPLICATION_NOT_ENOUGH_ARMORY_INFO)
            return
        
        applicant(applicants, ctx.author)["armory"] = ctx.message.content.split(None, 1)[1]
        await ctx.author.send(APPLICATION_PROVIDED_ARMORY)


@bot.command()
@commands.cooldown(1, 1, commands.BucketType.user)
async def raiderio(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        if len(ctx.message.content.strip().split(" ")) <= 1:
            await ctx.author.send(APPLICATION_NOT_ENOUGH_RAIDERIO_INFO)
            return
        
        applicant(applicants, ctx.author)["raiderio"] = ctx.message.content.split(None, 1)[1]
        await ctx.author.send(APPLICATION_PROVIDED_RAIDERIO)


@bot.command()
@commands.cooldown(1, 1, commands.BucketType.user)
async def logs(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        if len(ctx.message.content.strip().split(" ")) <= 1:
            await ctx.author.send(APPLICATION_NOT_ENOUGH_LOGS_INFO)
            return
        
        applicant(applicants, ctx.author)["logs"] = ctx.message.content.split(None, 1)[1]
        await ctx.author.send(APPLICATION_PROVIDED_LOGS)


@bot.command()
@commands.cooldown(1, 1, commands.BucketType.user)
async def why(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        if len(ctx.message.content.strip().split(" ")) <= 1:
            await ctx.author.send(APPLICATION_NOT_ENOUGH_WHY_INFO)
            return
        
        applicant(applicants, ctx.author)["why"] = ctx.message.content.split(None, 1)[1]
        await ctx.author.send(APPLICATION_PROVIDED_WHY)


@bot.command()
@commands.cooldown(1, 1, commands.BucketType.user)
async def xp(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        if len(ctx.message.content.strip().split(" ")) <= 1:
            await ctx.author.send(APPLICATION_NOT_ENOUGH_XP_INFO)
            return
        
        applicant(applicants, ctx.author)["xp"] = ctx.message.content.split(None, 1)[1]
        await ctx.author.send(APPLICATION_PROVIDED_XP)

@bot.command(pass_context=True)
@commands.cooldown(1, 1, commands.BucketType.user)
async def exp(ctx):
    await xp.invoke(ctx)
        
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def done(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        applicant_map = applicant(applicants, ctx.author)

        if "done" in applicant_map:
            await ctx.author.send(APPLICATION_SUBMIT_ALREADY)
            return

        if "armory" not in applicant_map:
            await ctx.author.send(APPLICATION_SUBMIT_MISSING_ARMORY)
            return

        if "raiderio" not in applicant_map:
            await ctx.author.send(APPLICATION_SUBMIT_MISSING_RAIDERIO)
            return

        if "logs" not in applicant_map:
            await ctx.author.send(APPLICATION_SUBMIT_MISSING_LOGS)
            return

        if "why" not in applicant_map:
            await ctx.author.send(APPLICATION_SUBMIT_MISSING_WHY)
            return

        if "xp" not in applicant_map:
            await ctx.author.send(APPLICATION_SUBMIT_MISSING_XP)
            return

        guild = bot.get_guild(DISCORD_GUILD)
        role = discord.utils.get(guild.roles, name=GuildRoles.ROLE_APPLICANT)
        member = await guild.fetch_member(ctx.author.id)
        
        await member.add_roles(role)
        
        applicant_map["done"] = datetime.now().strftime("%D")

        await ctx.author.send(APPLICATION_SUBMITTED)
        channel = bot.get_channel(DISCORD_APPLICATION_CHANNEL)

        message = APPLICATION_ACCEPTED.format(datetime.now().strftime("%D"), ctx.author, applicant(applicants, ctx.author)["armory"], applicant(applicants, ctx.author)["raiderio"], applicant(applicants, ctx.author)["logs"], applicant(applicants, ctx.author)["why"], applicant(applicants, ctx.author)["xp"])
        
        if len(message) > 2000:
           for each in message.split("$split"):
                await channel.send(each[:2000]) # Anything larger than this will be cut off due to discord limit
        else:
            await channel.send(message.replace("$split", ""))


@bot.command(pass_context=True)
@commands.has_any_role('Hand', 'Crusader', 'Sentinel', 'High Hand', 'Councillor')
@commands.cooldown(2, 5, commands.BucketType.user)
async def friend(ctx):
    role = discord.utils.get(bot.get_guild(DISCORD_GUILD).roles, name=GuildRoles.ROLE_FRIEND)
    member = ctx.message.mentions[0]

    if role in member.roles:
        await ctx.send(FRIEND_ROLE_ALREAD_ASSIGNED)
    else:
        await member.add_roles(role)
        await ctx.send(FRIEND_ROLE_ASSIGNED)

@bot.command(pass_context=True)
@commands.has_any_role('Crusader', 'Sentinel', 'High Hand', 'Councillor')
@commands.cooldown(2, 5, commands.BucketType.user)
async def dj(ctx):
    role = discord.utils.get(bot.get_guild(DISCORD_GUILD).roles, name=GuildRoles.ROLE_DJ)
    member = ctx.author

    if role in member.roles:
        await ctx.send(DJ_ROLE_ALREADY)
    else:
        await member.add_roles(role)
        await ctx.send(ASSIGN_DJ_ROLE)

@bot.command(pass_context=True)
@commands.has_any_role('Councillor')
@commands.cooldown(2, 5, commands.BucketType.user)
async def accept(ctx):
    role = discord.utils.get(bot.get_guild(DISCORD_GUILD).roles, name=GuildRoles.ROLE_INITIATE)
    member = ctx.message.mentions[0]
    channel = bot.get_channel(DISCORD_APPLICATION_CHANNEL)
    await ctx.send(APPLICATION_ACCEPTED_RESPONSE.format(member))
    await member.add_roles(role)
    await channel.send(APPLICATION_ACCEPTED.format(datetime.now().strftime("%D"), member.mention()))


@bot.command(pass_context=True)
@commands.has_any_role('Councillor')
@commands.cooldown(2, 5, commands.BucketType.user)
async def reject(ctx):
    role = discord.utils.get(bot.get_guild(DISCORD_GUILD).roles, name=GuildRoles.ROLE_APPLICANT)
    member = ctx.message.mentions[0]
    
    if role not in member.roles:
        await ctx.send(APPLICATION_REJECTED_NOT_APPLICANT.format(member))
        return

    reason = APPLICATION_DEFAULT_REJECTION_REASON
    if len(ctx.message.content.strip().split(" ")) >= 3:
        reason = ctx.message.content.split(None, 2)[2]
        
    await ctx.send(APPLICATION_REJECTED_RESPONSE.format(member))
    await member.remove_roles(role)
    await member.send(APPLICATION_REJECTED.format(member, reason))


@bot.command(pass_context=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def feedback(ctx):
    if len(ctx.message.content.strip().split(" ")) <= 1:
        await ctx.author.send(FEEDBACK_NOT_ENOUGH_PARAMS)
        return

    await ctx.author.send(FEEDBACK_RECEIVED)
    channel = bot.get_channel(DISCORD_OFFICER_CHANNEL)
    await channel.send(FEEDBACK_FORWARD.format(ctx.message.content.split(None, 1)[1]))

@bot.command(pass_context=True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def sentinels(ctx):
    await ctx.send(bot_wow_api.parse(SENTINELS))
    
@bot.command(pass_context=True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def raiders(ctx):
    await ctx.send(bot_wow_api.parse(RAIDERS))
    
@bot.command(pass_context=True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def roster(ctx):
    await ctx.send(bot_wow_api.parse(ROSTER))
    
@bot.command(pass_context=True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def council(ctx):
    await ctx.send(bot_wow_api.parse(COUNCIL))
    
@bot.command(pass_context=True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def initiates(ctx):
    await ctx.send(bot_wow_api.parse(INITIATES))
    
@bot.command(pass_context=True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def trials(ctx):
    await initiates.invoke(ctx)
    
@bot.command(pass_context=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def rules(ctx):
    await ctx.author.send(RULES)

@bot.command(pass_context=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def menu(ctx):
    await rules.invoke(ctx)

@bot.command(pass_context=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def help(ctx):
    await rules.invoke(ctx)


@bot.command(pass_context=True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def ranks(ctx):
    await ctx.send(RANKS)


@bot.command(pass_context=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def roles(ctx):
    await ranks.invoke(ctx)


@bot.command(pass_context=True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def alts(ctx):
    await ctx.send(ALTS)


@bot.command(pass_context=True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def prep(ctx):
    await ctx.send(PREPARATION_1)
    await ctx.send(PREPARATION_2)


@bot.command(pass_context=True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def addons(ctx):
    await ctx.send(ADDONS)


@bot.command(pass_context=True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def times(ctx):
    await ctx.send(TIMES)


@bot.command(pass_context=True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def about(ctx):
    await ctx.send(ABOUT)

@bot.command(pass_context=True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def play(ctx):
    await ctx.send("Coming soon! I don't support it yet though =/")

# bot_music.setup(bot)

bot.run(os.getenv('DISCORD_TOKEN'))
