import discord
import os
import modules.ExtFuncs as util
import modules.checks as customChecks
import json
import threading
import multiprocessing
import modules.twitchBot as twitchBot
from discord.ext import commands
from twitchio.ext import commands as twitchComs
import twitchio

twitchProcessName = 'twitchBot'

class botClass:
    def __init__(self, gid):
        self.guildId = gid
        self.twitchChannel = self.getChannel()

    def getChannel(self):
        getGlob = util.globalVars()
        return getGlob.streamers.get(str(self.guildId))

class twitchBotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.processes = []
        self.shareData = multiprocessing.Queue()


    @commands.command(name='runTwitch')
    @customChecks.checkRole('Admins')
    async def runTwitch(self, ctx):
        gid = ctx.guild.id
        globVars = util.globalVars()
        streamers = globVars.streamers
        botData = botClass(gid)

        if streamers.get(str(gid)) != None:
            processName = f'{twitchProcessName}-{gid}'
            twitchProcess = multiprocessing.Process(target=twitchBot.run, kwargs={'botClass': botData.twitchChannel, 'guildId': botData.guildId, 'dataQueue': self.shareData}, name=processName)
            twitchProcess.start()
            self.processes.append(processName)
            await ctx.send(f'Twitch Bot has been started on the channel "{streamers.get(str(gid))}"')
        else:
            await ctx.send(f'The guild {ctx.guild.name} does not have an associated twitch channel...')
    
    def cog_unload(self):
        for process in self.processes:
            print(f'Terminating process: {process.name}')
            process.join()
        print('unloaded cog')

def setup(bot):
    bot.add_cog(twitchBotCog(bot))