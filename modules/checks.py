
import discord
from discord.ext import commands
import twitchio
from twitchio.ext import commands as twitchComs
from modules import ExtFuncs

# Checks if a user has a role in a list of roles
def checkRole(roleObj):
    def predicate(ctx):
        roleList = ((ExtFuncs.readVars(ctx.guild.id)).get('Roles')).get(roleObj)
        for role in roleList:
            if commands.has_role(role):
                return True
            elif ctx.author ==  ctx.guild.owner:
                return True
            else:
                continue
        return False
    return commands.check(predicate)

# Checks if a user is @SDarkMagic
def checkUserDark():
    def predicate(ctx):
        if ctx.author.id == 384331331527639042:
            return True
        else:
            return False
    return commands.check(predicate)

# Checks if user is the server owner
def checkOwner():
    def predicate(ctx):
        print(ctx.guild.owner)
        if ctx.author ==  ctx.guild.owner:
            return True
        else:
            return False
    return commands.check(predicate)

# Checks if a user is a twitch channel moderator
def checkMod():
    def predicate(ctx):
        if ctx.author.is_mod:
            return True
        else:
            return False
    return twitchComs.check(predicate)