# bot.py
import discord
from discord.ext import commands
import os
import modules.ExtFuncs as ExtFuncs
import modules.TwitchAPI as TwitchAPI
import modules.checks as customChecks
import time
import requests
import json
import asyncio
import sys
from googlesearch import search
from datetime import datetime
import googletrans
import pathlib
import threading
#import twitchBot
import re
from asgiref import sync

# Global Variables
botStartTime = datetime.now()
token = os.getenv('TOKEN')
cli = discord.Client()
bot = commands.Bot(
    command_prefix=os.environ['PREFIX'],
    guild_subscriptions=True
    )
varPath = pathlib.Path('Vars')
TWITCH_STREAM_API_ENDPOINT = "https://api.twitch.tv/helix/streams/"
loopVar = True
now = botStartTime.strftime("%Y-%m-%d").replace('/', '')
errorLog = open(pathlib.Path(f'logs/errors/{str(now)}-ErrorLog.txt'), "wt")
errorLog.close()
rolesVar = []
nativeLang = 'en'
languages = googletrans.LANGUAGES   
path = pathlib.Path('.')
threads = []
botLoop = asyncio.new_event_loop()
killThread = False

# Attempts to load cogs located in modules/cogs
def loadCogs():
    cogDir = path / 'modules/discordCogs'
    for file in os.listdir(cogDir):
        if (str(file).split('.')[-1]) == (str('py')):
            currentCog = f'modules.discordCogs.{str(file)[:-3]}'
            try:
                bot.load_extension(currentCog)
                print(f'Successfully loaded cog "{currentCog}"')
            except:
                print(f'Failed to load cog "{currentCog}"')
                continue
        else:
            print(f'{str(file).split(".")} is not a python file, and thus could not be loaded as a cog.')
#    print(f"comparing {(str(file).split('.'))} and {(str('py'))}")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    TwitchAPI.getOauth()
    initThreads()
#    refreshauth = asyncio.create_task(roa())
    log = asyncio.create_task(logName())
#    twitchBot = asyncio.create_task(os.system('pipenv run python twitchBot.py'))
    loadCogs()

    await asyncio.gather(
#        refreshauth,
        log
    )
    await bot.change_presence(activity=discord.Game(name='Beta'))

# Runs every time a message is sent
@bot.event
async def on_message(ctx):
    await event_message_log(ctx)
    if (ctx.author == bot.user):
        print("The bot is not allowed to respond to itself")
        return
    else:
#        await event_yeetMeow(ctx)
        await event_filter(ctx)
        await event_magic(ctx)
        await event_creeper(ctx)
        await bot.process_commands(ctx)
        

class sendAnnouncement:
    def __init__(self, dataToSend):
        self.dataToSend = dataToSend
        self.dataStatus, self.dataTypes, self.objId = self.checkDataIn()
        try:
            self.runningLoop = asyncio.get_running_loop()
        except:
            self.runningLoop = None

        if self.runningLoop != None:
            self.runningLoop = self.runningLoop
        else:
            self.runningLoop = asyncio.new_event_loop()
        
        asyncio.set_event_loop(self.runningLoop)
        self.client = None

    async def runLoop(self):
        self.client = discord.Client()

        @self.client.event
        async def on_ready():
            print(f'{self.client.user} connected successfully!')
            channel = self.client.get_channel(int(self.objId))
            await channel.send(content=str(self.dataToSend.get('content')), embed=self.dataToSend.get('embed'))
            await self.client.close()
            await self.client.logout()

        await self.client.login(token)
        await self.client.connect()

    def checkDataIn(self):
        dataTypes = {}
        if isinstance(self.dataToSend, dict):
            try:
                objId = self.dataToSend.get('id')
            except:
                return(False)

            if objId != None:
                if self.dataToSend.get('content') != None:
                    dataTypes.update({'content': True})
                else:
                    dataTypes.update({'content': False})

                if self.dataToSend.get('embed') != None:
                    dataTypes.update({'embed': True})
                else:
                    dataTypes.update({'embed': False})   
                return(True, dataTypes, objId)
            else:
                return(False)
        else:
            return(False)

    async def sendMessage(self):
        print(self.dataStatus)
        for key in self.dataTypes.keys():
            if self.dataTypes.get(key) == False:
                self.dataToSend.update({key: None})
            else:
                continue
        if self.dataStatus == True:
            await self.runLoop()
            return
        else:
            return
    
    def callSendMsg(self):
        asyncio.run(self.sendMessage())


# Initiates threads for stream live checks
def initThreads():
    global threads
    streamerGuilds = []
    gen = open(pathlib.Path('Vars/globalVars.json'), 'rt')
    currentGuilds = json.loads(gen.read()).get('TwitchChannel')
    gen.close()
    for x in currentGuilds.keys():
        if currentGuilds.get(x) != None:
            streamerGuilds.append(x)
        else:
            continue
    for guildObj in bot.guilds:
        guildId = guildObj.id
        if str(guildId) in streamerGuilds:
            newThread = threading.Thread(target=check_live, kwargs={'guild': guildId}, name=guildId)
            threads.append(newThread)
            newThread.start()
        else:
            continue

# Checks if the admin's twitch channel is live
def check_live(guild, loopVar=None):
    print('called check_live')
    if loopVar == None:
        loopVar = True
    dcBackendFile = open(pathlib.Path(f'Vars/{guild}/{guild}.json'), 'rt')
    dcBackend = (json.loads(dcBackendFile.read())).get('DiscordBackend')
    adminName = dcBackend.get('streamTTVChannel')
    while loopVar == True:
        if killThread:
            break
        else:
            if (TwitchAPI.checkUser(adminName.lower()) == True):
                embedSend=(TwitchAPI.generateEmbed(adminName.lower()))
                messageDict = {'id': dcBackend.get('streamAnnouncementChannel'), 'content': (dcBackend.get('streamAnnouncementRole') + "\n"), 'embed': embedSend}
                initAnnounce = sendAnnouncement(messageDict)
                print('set initAnnounce variable')
                initAnnounce.callSendMsg()
                print('made call to run send message function')
                time.sleep(300)
                loopVar = False
                check_offline(guild, loopVar)
            else:
                time.sleep(30)
   
# Checks for the channel to go offline before sending another message
def check_offline(guild, loopVar):
    dcBackendFile = open(pathlib.Path(f'Vars/{guild}/{guild}.json'), 'rt')
    dcBackend = (json.loads(dcBackendFile.read())).get('DiscordBackend')
    adminName = dcBackend.get('streamTTVChannel')
    while loopVar == False:
        if killThread:
            break
        else:
            if (TwitchAPI.checkUser(adminName.lower()) == True):
                time.sleep(30)
            else:
                loopVar = True
                time.sleep(300)
                check_live(guild, loopVar)

"""
# Automatically refreshes the oauth token
async def roa():
    currentTasks = asyncio.all_tasks()
    timeLeft = TwitchAPI.authTimeLimit()
    timeTilRefresh = timeLeft - 15
    if streamStatus in currentTasks:
        streamStatus.cancel()
        streamStatus = asyncio.create_task(check_live())
    await asyncio.sleep(timeTilRefresh)
    
    TwitchAPI.getAccessToken()
"""

# Updates the log file name hourly
async def logName():
    global logNameVar
    now = datetime.now()
    formattedNow = now.strftime("%d-%m-%Y_%H")
    logNameVar = str(formattedNow + '_log.csv')
    await asyncio.sleep(3600)
    

# Filter
@bot.event
async def event_filter(ctx):
    if ctx.guild != None:
        openVars = open(pathlib.Path(f'Vars/{ctx.guild.id}/{ctx.guild.id}.json'), 'rt')
        load = json.loads(openVars.read())
        openVars.close()
        admin = bot.get_user((load.get('DiscordBackend').get('adminUserId')))
        bannedWordsList = load.get('BannedWords')
    else:
        return
#    bannedwordregex = re.compile

    print("Running filter")
    if (ctx.author == bot.user):
        print("The message was sent by the bot, and thus was ignored by the filter.")
        return
    else:
        msgToList = ctx.content.split(" ")
        for item in msgToList:
            itemFinal = ExtFuncs.puncStrip(item)
            if (str(itemFinal).lower() in bannedWordsList):
                await ctx.delete()
                await ctx.channel.send(ctx.author.mention + " Please refrain from using that language.")
                await admin.send(ctx.author.name + ' said: ' + ctx.content)
            else:
                continue

# Magic
@bot.event
async def event_magic(ctx):
    msgToList = ctx.content.split(" ")
    for item in msgToList:
        if (item.lower() == 'magic'):
            await ctx.channel.send(ctx.author.mention + " *Dark Magic")
            break
        else:
            continue
#            print(ctx.author)

# Creeper
@bot.event
async def event_creeper(ctx):
    msgToList = ctx.content.split(" ")
    for item in msgToList:
        if (item.lower() == 'creeper'):
            await ctx.channel.send("Aww Man")
"""
# Yeet the meow
async def event_yeetMeow(ctx):
    msgList = ctx.content.split(" ")
    for item in msgList:
        itemFinal = ExtFuncs.puncStrip(item)
        if itemFinal.lower() == 'meow':
            await ctx.delete()
            await ctx.author.send("don't use that word")
"""

# Message logging
async def event_message_log(ctx):
    if ctx.guild != None:
        logPath = pathlib.Path(varPath / str(ctx.guild.id) / 'logs')
    else:
        logPath = pathlib.Path('logs/Discord')
    ExtFuncs.log(logPath, logNameVar, ctx.author, ctx.channel, ctx.content)

# Checks for a command that errored out
@bot.event
async def on_command_error(ctx, error):
    errorLog = open(pathlib.Path(f'logs/errors/{str(now)}-ErrorLog.txt'), "at")
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the permissions to use this command.')
    elif isinstance(error, commands.errors.CommandError):
        await ctx.send("An unexpected error occured...")
        print(error)
    errorLog.write(str(error) + "\n")
    errorLog.close()

# Runs whenever the bot joins a server
@bot.event
async def on_guild_join(ctx):
    guildID = str(ctx.id)
    blankDict = {"Links": {}, "DiscordBackend": {}, "Roles": {"Admins": [], "Moderators": []}, "TwitchData": {}, "BannedWords": []}
    os.mkdir(pathlib.Path(varPath / guildID))
    os.mkdir(pathlib.Path(varPath / guildID / 'logs'))
    guildVarFile = varPath / guildID / f'{guildID}.json'
    if guildVarFile.exists():
        return
    else:
        initVars = open(guildVarFile, 'wt')
        initVars.write(json.dumps(blankDict, indent=2))
        initVars.close()
    with open('Vars/globalVars.json', 'rt') as general:
        generalVars = json.loads(general.read())
        print(generalVars)
        general.close()
    with open('Vars/globalVars.json', 'wt') as writeGen:
        streamers = generalVars.get('TwitchChannel')
        streamers.update({guildID: None})
        generalVars.update({'TwitchChannel': streamers})
        writeGen.write(json.dumps(generalVars, indent=2))
        writeGen.close()

# Runs everytime the bot leaves and/or gets kicked or banned from a server
@bot.event
async def on_guild_remove(ctx):
    guildID = str(ctx.id)
    guildVarFile = pathlib.Path(varPath / guildID / f'{guildID}.json')
    try:
        for fileObj in pathlib.Path(varPath / guildID / 'logs').iterdir():
            os.remove(fileObj)
        os.rmdir(pathlib.Path(varPath / guildID / 'logs'))
        os.remove(guildVarFile)
        os.rmdir(pathlib.Path(varPath / guildID))
    except:
        print(f'The file: {guildVarFile} could not be found, and thus was not deleted.')

    with open('Vars/globalVars.json', 'rt') as general:
        generalVars = json.loads(general.read())
        general.close()
    with open('Vars/globalVars.json', 'wt') as writeGen:
        streamers = generalVars.get('TwitchChannel')
        streamers.pop(guildID)
        generalVars.update({'TwitchChannel': streamers})
        writeGen.write(json.dumps(generalVars, indent=2))
        writeGen.close()


# Runs everytime a new member joins a server
@bot.event
async def on_member_join(ctx):
    print('new member')
    varFile = open(pathlib.Path(varPath / f'{ctx.guild.id}/{ctx.guild.id}.json'), 'rt')
    dcBackend = (json.loads(varFile.read())).get('DiscordBackend')
    varFile.close()
    userRoles = ctx.roles
    try:
        lockRole = ctx.guild.get_role(int(dcBackend.get('lockRole')))
        userRoles.append(lockRole)
    except:
        print(f'No lock role for server {ctx.guild}')
#    varFile = open(pathlib.Path(f'Vars/{ctx.guild.id}/{ctx.guild.id}.json'))
    welcomeChannel = bot.get_channel(int((json.loads(varFile.read()).get("DiscordBackend")).get("WelcomeChannel")))
    await welcomeChannel.send(f'{ctx.mention} welcome to {ctx.guild.name}. We hope you enjoy your stay here!')
    await ctx.edit(roles=userRoles)
    


# A test command subject to change
@bot.command(name="test")
async def test(ctx, user='sdarkmagic'):
    await bot.change_presence(activity=discord.Game(name='YEP'))
    streamEmbed = TwitchAPI.generateEmbed(user)
    testEmbed = discord.Embed(
        title='SDarkMagic Just Went live!',
        description="waow",
        url=os.getenv('TWITCH'),
        color=discord.Color(0xB345E2)
    )
    Channel = discord.Client.get_channel(bot, id=int(os.getenv('STREAM_ANNOUNCEMENT_CHANNEL')))
    print(Channel)
    await ctx.trigger_typing()
    time.sleep(2)
    await ctx.send(embed=streamEmbed)

# Shuts down the bot
@bot.command(name="shutDown", aliases=["sd", "shutdown", "Sd", "sD"])
@customChecks.checkUserDark()
async def shutDown(ctx):
    await ctx.send("Bot shutting down!")
    safeShutDown()
    await bot.logout()
    await bot.close()
    sys.exit()

# Checks messages for non-english content
@bot.command(name='translate')
async def translate(ctx, *phrase):
    phrase = " ".join(phrase[:])
    detect = googletrans.Translator().detect(phrase)
    if(detect.lang == nativeLang):
        await ctx.send("Message was already in English.")
        return
    else:
        print(detect.lang)
        translated = googletrans.Translator().translate(phrase, dest=nativeLang, src=detect.lang)
        await ctx.channel.trigger_typing()
        await ctx.channel.send(ctx.author.name + ' said: '+ translated.text + '\n' + str(languages.get(detect.lang)))

# Sends a message containing a link to my GB profile
@bot.command(name="gb", aliases=["GB", "gameBanana", "GameBanana", "gamebanana"])
async def gb(ctx):
    await ctx.send("Here is a link to " + adminName + "'s GameBanana profile!\n" + GBLink)

# Sends a message containing a link to Twitch channel
@bot.command(name="twitch")
async def twitch(ctx):
    await ctx.send(adminName + "'s can be found at " + twitchLink)

# Sends a message containing a link to YT channel
@bot.command(name="youtube", aliases=["yt"])
async def youtube(ctx):
    await ctx.send(adminName + "'s Youtube channel can be found at " + ytLink)

# Googles and returns the top 5 links in a list
@bot.command(name="getLink")
async def getLink(ctx, *query):
    await ctx.trigger_typing()
    searchStr = " ".join(query[:])
    googSearch = search(searchStr, tld="com", lang="en", num=5, stop=5)
    msg = ctx.author.mention + ' Here are some links to your search for "' + searchStr + '"\n'
    for link in googSearch:
        print(link)
        msg = msg + "<" + link + ">\n"
    await ctx.send(msg)

# Refreshes the twitch OAUTH token
@bot.command(name="refreshOauth", aliases=["ROAUTH", "ROA"])
@customChecks.checkUserDark()
async def refreshOauth(ctx):
    TwitchAPI.getOauth()
    await ctx.send('Twitch Oauth Token regenerated successfully.')

"""
@bot.command(name='bmpm', aliases=['bulkReplace'])
async def bmpm(ctx):
    """

# Sends admin a copy of the chat log
@bot.command(name='viewLog')
@customChecks.checkRole('Moderators')
async def viewLog(ctx):
    logPath = pathlib.Path(f'{varPath}/{ctx.guild.id}/logs')
    fileName = pathlib.Path(str(logPath / logNameVar)).resolve()
    openFile = open(fileName, 'rb')
    fileUp = discord.File(openFile)
    await ctx.author.send('Here is a copy of the chat log found at: ' + str(fileName), file=fileUp)

# Reloads a cog
@bot.command(name='reloadCog', aliases=['rc'])
@customChecks.checkUserDark()
async def reloadCog(ctx, cogName):
    bot.unload_extension(f'modules.discordCogs.{cogName}')
    bot.load_extension(f'modules.discordCogs.{cogName}')
    await ctx.send(f'Successfully reloaded the cog {cogName}.')

# Unloads a cog
@bot.command(name='unloadCog', aliases=['uc'])
@customChecks.checkUserDark()
async def unloadCog(ctx, cogName):
    bot.unload_extension(f'modules.discordCogs.{cogName}')
    await ctx.send(f'Successfully unloaded the cog {cogName}.')

# Unloads a cog
@bot.command(name='loadCog', aliases=['lc'])
@customChecks.checkUserDark()
async def loadCog(ctx, cogName):
    bot.load_extension(f'modules.discordCogs.{cogName}')
    await ctx.send(f'Successfully loaded the cog {cogName}.')

# restarts the bots system using the 'rebootSequence()' function
@bot.command(name="systemReboot")
@customChecks.checkUserDark()
async def systemReboot(ctx):
    rebootSequence()
    await bot.close()

"""
# Starts the twitch bot end of things
@bot.command(name='runTwitch')
@customChecks.checkUserDark()
async def runTwitch(ctx):
    await ctx.send('Running Twitch Bot!')
    twitchThread = threading.Thread(target=twitchBot.main)
    twitchThread.start()
"""
"""
@bot.command(name="restart")
@commands.has_role("Owner(s)")
async def restart(ctx):
    await ctx.send("bot restarting")
    await bot.close()
    time.sleep(2)
    os.system("./home/pi/Desktop/runBots.sh")
"""
# Series of commands for restarting the system(only works if system is linux based)
def rebootSequence():
    os.system("sudo shutdown -r now")

def safeShutDown():
    global killThread
    killThread = True
    for threadObj in threads:
        threadObj.join()
        print(f'Successfully killed the thread: {threadObj.name}')
    for cogFile in pathlib.Path('modules/discordCogs').iterdir():
        if cogFile.name.split[-1] == 'py':
            try:
                print(f'unloading {cogFile.name}')
                bot.unload_extension(f'modules.discordCogs.{cogFile.name}')
            except:
                continue
        else:
            continue

def main():
    asyncio.set_event_loop(botLoop)
    bot.run(token)


if __name__ == "__main__":
    main()