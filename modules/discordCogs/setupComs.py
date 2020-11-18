import discord
import json
import pathlib
#import bot as botFunctions
import modules.checks as customChecks
import modules.ExtFuncs as util
from discord.ext import commands

class setupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @customChecks.checkRole('Admins')
    @commands.command(name='amStrimmer', aliases=['amStreamer'])
    async def amStrimmer(self, ctx, channelName=None):
        if channelName == None:
            await ctx.send('Please include a twitch channel name to check for live activity.')
        else:
            pass
        guildVarPath = util.filePath(ctx.guild.id)

        with open(pathlib.Path(f'Vars/globalVars.json'), 'rt') as readFile:
            existingData = json.loads(readFile.read())
            streamers = existingData.get('TwitchChannel')
            streamers.update({ctx.guild.id: channelName})
            existingData.update({'TwitchChannel': streamers})

        with open(pathlib.Path(f'Vars/globalVars.json'), 'wt') as writeFile:
            writeFile.write(json.dumps(existingData, indent=2))

        guildReadVars = guildVarPath.jsonData
        dcBackend = guildReadVars.get('DiscordBackend')
        dcBackend.update({'streamTTVChannel': channelName})
        guildReadVars.update({'DiscordBackend': dcBackend})
        defaultTwitchData = {'entryLines': [], 'missTxt': '', 'Rules': {}, 'CustomComs': {}, 'EasterEggs': False}

        try:
            twitchData = guildReadVars.get('TwitchChannel')
        except:
            twitchData = None
        if twitchData == None:
            twitchData = defaultTwitchData
        else:
            for key in defaultTwitchData:
                if key in twitchData:
                    continue
                else:
                    twitchData.update({key: defaultTwitchData.get(key)})
                    
        guildReadVars.update({'TwitchChannel': twitchData})

        with open(guildVarPath.jsonPath, 'wt') as guildWriteVarsFile:
            guildWriteVarsFile.write(json.dumps(guildReadVars, indent=2))
        await ctx.send(f'{ctx.guild.name} has been successfully added as a streaming server!')

    # Adds a word to the blacklist for a server
    @commands.command(name="blackList", aliases=['blacklist'])
    @customChecks.checkRole('Moderators')
    async def blackList(self, ctx, wordToBlacklist):
        fileOpenPath = pathlib.Path(f'Vars/{ctx.guild.id}/{ctx.guild.id}.json')
        guildVars = open(fileOpenPath, 'rt')
        jsonVars = json.loads(guildVars.read())
        blacklistedWords = list(jsonVars.get('BannedWords'))
        blacklistedWords.append(wordToBlacklist)
        jsonVars.update({'BannedWords': blacklistedWords})
        guildVars.close()
        with open(f'Vars/{ctx.guild.id}/{ctx.guild.id}.json', 'wt') as writeVarFile:
            writeVarFile.write(json.dumps(jsonVars, indent=2))
        await ctx.author.send(f"Successfully added the word {wordToBlacklist} to {ctx.guild.name}'s' blacklisted words!")

    # Adds a role to the moderator rolelist
    @customChecks.checkRole('Admins')
    @commands.command(name='addModRole', aliases=['setModRole'])
    async def addModRole(self, ctx, roleToAdd=None):
        print(roleToAdd)
        print(type(roleToAdd))
        if roleToAdd != None:
            pass
        else:
            await ctx.send('No role specified.')
            return
        filePath = util.filePath(ctx.guild.id)
        with open(filePath.jsonPath, 'rt') as readVars:
            varData = json.loads(readVars.read())
            roles = varData.get('Roles')
            mods = roles.get('Moderators')
        if isinstance(roleToAdd, discord.Role):
            roleToAdd = roleToAdd.id
        else:
            try:
                roleToAdd = int(roleToAdd)
            except:
                await ctx.send('Invalid role or role ID.')
                return
        mods.append(roleToAdd)
        roles.update({'Moderators': mods})
        varData.update({'Roles': roles})
        with open(filePath.jsonPath, 'wt') as writeVars:
            writeVars.write(json.dumps(varData, indent=2))
        await ctx.send(f'Successfully added {ctx.guild.get_role(roleToAdd).mention} as a mod role.')

    # Adds a role to the admin rolelist
    @customChecks.checkOwner()
    @commands.command(name='addAdminRole', aliases=['setAdminRole'])
    async def addAdminRole(self, ctx, roleToAdd=None):
        print(roleToAdd)
        print(type(roleToAdd))
        if roleToAdd != None:
            pass
        else:
            await ctx.send('No role specified.')
            return
        filePath = util.filePath(ctx.guild.id)
        with open(filePath.jsonPath, 'rt') as readVars:
            varData = json.loads(readVars.read())
            roles = varData.get('Roles')
            admins = roles.get('Admins')
        if isinstance(roleToAdd, discord.Role):
            roleToAdd = roleToAdd.id
        else:
            try:
                roleToAdd = int(roleToAdd)
            except:
                await ctx.send('Invalid role or role ID.')
                return
        admins.append(roleToAdd)
        roles.update({'Admins': admins})
        varData.update({'Roles': roles})
        with open(filePath.jsonPath, 'wt') as writeVars:
            writeVars.write(json.dumps(varData, indent=2))
        await ctx.send(f'Successfully added {ctx.guild.get_role(roleToAdd).mention} as an admin role.')

    # Sets the stream announcement Chanel to current channel or specified channel If
    @customChecks.checkOwner()
    @commands.command(name='setStreamAnnounceChannel')
    async def setStreamAnnounceChannel(self, ctx, channelId=None):
        filePath = util.filePath(ctx.guild.id)
        dcBackend = None
        with open(filePath.jsonPath, 'rt') as readGuildVarsFile:
            readGuildVars = json.loads(readGuildVarsFile.read())
            dcBackend = readGuildVars.get('DiscordBackend')
        print(type(channelId))
        if channelId == None:
            channelId = int(ctx.channel.id)
#        elif isinstance(channelId, str):
#            try:
#                channelId = ctx.guildchannelId.id
        else:
            try:
                channelId = int(channelId)
            except:
                await ctx.send('Invalid channel or channel ID.')
                return
        dcBackend.update({"streamAnnouncementChannel": channelId})
        readGuildVars.update({'DiscordBackend': dcBackend})
        with open(filePath.jsonPath, 'wt') as writeVarsFile:
            writeVarsFile.write(json.dumps(readGuildVars, indent=2))
        await ctx.send(f'Successfully set {ctx.guild.get_channel(channelId).mention} as the stream announcement channel.')

def setup(bot):
    bot.add_cog(setupCommands(bot))
