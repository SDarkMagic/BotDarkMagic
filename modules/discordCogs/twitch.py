import discord
import os
import modules.ExtFuncs as util
import modules.checks as customChecks
import json
import time
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
        self.processQueues = {}
        self.shareData = multiprocessing.Queue()
    

    @commands.command(name='runTwitch')
    @customChecks.checkRole('Admins')
    async def runTwitch(self, ctx):
        gid = ctx.guild.id
        globVars = util.globalVars()
        streamers = globVars.streamers
        botData = botClass(gid)

        if streamers.get(str(gid)) != None:
            shareData = multiprocessing.Queue()
            processName = f'{twitchProcessName}-{gid}'
            twitchProcess = multiprocessing.Process(target=twitchBot.run, kwargs={'botClass': botData.twitchChannel, 'guildId': botData.guildId, 'dataQueue': shareData}, name=processName)
            twitchProcess.start()
            self.processQueues.update({gid: [twitchProcess, shareData]})
            await ctx.send(f'Twitch Bot has been started on the channel "{streamers.get(str(gid))}"')
        else:
            await ctx.send(f'The guild {ctx.guild.name} does not have an associated twitch channel...')

    @commands.command(name='endTwitch', aliases=['killTwitch'])
    @customChecks.checkRole('Admins')
    async def endTwitch(self, ctx):
        gid = ctx.guild.id
        guildProcess = self.processQueues.get(gid)
        queue = guildProcess[-1]
        process = guildProcess[0]
        queue.put(True)
        time.sleep(6)
        print(f'Terminating process: {str(process)}')
        process.terminate()
        process.join()
        print('joined process')
        process.close()
        print('closed process')
        self.processQueues.pop(gid)
        await ctx.send('Successfully ended the twitch bot!')

    
    def cog_unload(self):
        for queue in self.processQueues.values():
            try:
                queue[-1].put(True)
            except:
                continue
        for process in self.processQueues.keys():
            print(f'Terminating process: {str(process)}')
            currentProcess = self.processQueues.get(process)[0]
            time.sleep(6)
            currentProcess.terminate()
            currentProcess.join()
            print('joined process')
            currentProcess.close()
            print('closed process')
        print('unloaded cog')

def setup(bot):
    bot.add_cog(twitchBotCog(bot))