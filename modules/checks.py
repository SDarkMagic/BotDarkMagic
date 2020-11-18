
import discord
from discord.ext import commands
import twitchio
import functools
from twitchio.ext import commands as twitchComs
from modules import ExtFuncs
from discord.ext.commands import errors

# Checks if a user has a role in a list of roles
def checkRole(roleObj):
    def predicate(ctx):        
        items = ((ExtFuncs.readVars(ctx.guild.id)).get('Roles')).get(roleObj)
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            raise errors.NoPrivateMessage()
        getter = functools.partial(discord.utils.get, ctx.author.roles)
        if any(getter(id=item) is not None if isinstance(item, int) else getter(name=item) is not None for item in items):
            return True
        raise errors.MissingAnyRole(items)
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