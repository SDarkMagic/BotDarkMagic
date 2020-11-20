# bot.py
import os
import random
import time
import modules.ExtFuncs as ExtFuncs
import twitchio
from twitchio.ext import commands
import json
import datetime
import pathlib
import sys
import threading
import asyncio
import checks as customChecks
import nest_asyncio
nest_asyncio.apply()

initChannels = ['BotDarkMagic']
runningThreads = []
killThread = False

class dataChecker:
    def __init__(self, data):
        self.queue = data
        self.threadName = f'Twitch_{gid}_A'

    def check(self):
        global runningThreads
        self.thread = threading.Thread(name=self.threadName, target=self.checkLoop)
        runningThreads.append(self.thread)
        self.thread.start()

    def checkLoop(self):
        print('checkLoop running')
        checkData = self.getPutData()
        print(checkData)
        async def sendKill():
            await bot._ws.send_privmsg(channelToJoin[0], '!exit')
            return

        if checkData == True or killThread == True:
            if checkData == True:
                asyncio.run(sendKill())
            else:
                pass
            return
        else:
            time.sleep(30)
            self.checkLoop()

    def getPutData(self):
        try:
            dataDown = self.queue.get(True, 5)
        except:
            dataDown = None
            return dataDown
        self.queue.put(dataDown)
        print(f'dataDown: {dataDown}')
        return dataDown


def run(botClass, guildId, dataQueue):
    print('called run')
    global data
    global channelToJoin
    global gid
    data = dataQueue
    channelToJoin = [botClass]

    if botClass != None:
        gid = guildId
    else:
        print('No way to share data between discord and twitch; Killing twitch bot process')
        return
    bot.run()

bot = commands.Bot(
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=initChannels,
    )

# Global Variables
now = time.strftime("%Y-%m-%d_%H%M%S")
me = "/me "
deathCounter = 0
gid = None

# Bot Events

@bot.event
async def event_ready():
    global checker
    'Called once when the bot goes online.'
    print(f"{os.environ['BOT_NICK']} is now online!")
    await joinChannel(channelToJoin)
    await bot.part_channels(initChannels)
    varData = ExtFuncs.filePath(gid).twitchData
    try:
        randomEntrance = random.choice(varData.get('entryLines'))
    except:
        randomEntrance = f'No custom entrance lines for the bot were found. To add some, please use the command "!addEntry <text for bot to say when joining the chat>"'
    if ExtFuncs.filePath(gid).twitchData.get('EasterEggs'):
        bot.load_module('modules.twitchCogs.easterEggs')
    else:
        pass
    print(randomEntrance)
    checker = dataChecker(data)
    checker.check()
    ws = bot._ws
    await ws.send_privmsg(channelToJoin[0], f"/me {randomEntrance}")

@bot.event
async def event_message(ctx):
    'Runs every time a message is sent in chat.'
    # make sure the bot ignores it and the streamer
    if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
#        await event_log(ctx)
        if ctx.content == '!exit':
            await bot.part_channels(channelToJoin)
            safeShutDown()
        else:
            return
    else:
        try:
            await handle_customComs(ctx)
        except:
            await bot.handle_commands(ctx)
        await event_filter(ctx)
#        await event_log(ctx)

async def handle_customComs(ctx):
    guildData = customComs(gid)
    messageList = ctx.content.split(' ')
    if messageList[0].startswith('!'):
        command = str(messageList[0]).lstrip('!')
        if guildData.searchComs(command):
            await ctx.channel.send(guildData.customComs.get(command))
        else:
            raise commands.errors.CommandNotFound(f'<{command}> was not found.')
    else:
        raise commands.errors.CommandNotFound(f'<{command}> was not found.')

# Chat filter
async def event_filter(ctx):
    # A function to read every message and moderate based off of a predetermined list of words
    bannedWordsList = ExtFuncs.filePath(gid).bannedWords
    for listObj in bannedWordsList:
        listObjIndex = bannedWordsList.index(listObj)
        listObj = listObj.rstrip("\n")
        bannedWordsList[listObjIndex] = listObj
    userName = ctx.author.name
    print("Running filter")
    if (ctx.author.name.lower() == os.environ['BOT_NICK'].lower() or ctx.author.is_mod == True):
        print("The message was sent by the channel owner, a moderator, or the bot, and thus was ignored by the filter.")
        return
    else:
        msgToList = ctx.content.split(" ")
#        print(msgToList)
        for item in msgToList:
            itemFinal = ExtFuncs.puncStrip(item)
            if (str(itemFinal).lower() in bannedWordsList):
                await ctx.channel.send("@" + userName + " Please refrain from using that language.")
                await ctx.channel.timeout(userName, 30, "Poor choice of words...")
            else:
                continue
"""
# Chat log
async def event_log(ctx):
    # A function for logging all messages in the chat to a text file
    path = pathlib.Path(f'{gid}/logs/Twitch')
    ExtFuncs.log(path, str(datetime.datetime.now().strftime("%Y-%m-%d").replace('/', '') + '.csv'), ctx.author.name, 'SDarkMagic-Twitch', str(ctx.content.replace(',', '')))
"""

# Runs whenever there is a subscription
@bot.event
async def event_usernotice_subscription(ctx):
    print(ctx)


# Bot Commands

"""
# Displays channel emotes in chat
@bot.command(name="emotes")
async def emotes(ctx):
    emoteList = (json.loads(open('twitchChannel.json', 'rt').read())).get('emotes')
    print(emoteList)
#    print(emoteList) #sends the list as a chat message
    msg = "/me Emotes available on this channel through BTTV include, but aren't limited to: "
    for emote in emoteList:
        msg = msg + emote + " "
    await ctx.send(msg)

# Adds an emote
@bot.command(name="addEmote")
async def addEmote(ctx, emote):
    emoteDict = json.loads(open('twitchChannel.json', 'rt').read())
    emoteList = emoteDict.get('emotes')
    if (ctx.author.name.lower() == os.environ["CHANNEL"].lower() or ctx.author.is_mod == True):
        emoteFile = open('twitchChannel.json', 'wt')
#        print ("You can use this command!")
#        print(emote)
        emoteList.append(emote)
        emoteDict.update({'emotes': emoteList})
        emoteFile.write(json.dumps(emoteDict, indent=2))
        await ctx.send("The emote, " + emote + " has been successfully added.")
        emoteFile.close()
    else:
        await ctx.send("You don't have the permissions to use this command!")


# Removes an emote
@bot.command(name="removeEmote")
async def removeEmote(ctx, emote):
    emoteDict = json.loads(open('twitchChannel.json', 'rt').read())
    emoteList = emoteDict.get('emotes')
    if (ctx.author.name.lower() == os.environ["CHANNEL"].lower() or ctx.author.is_mod == True):
        #        print("You can use this command!")
        #        print(emote)
        #        print(emoteList)
        if (emote in emoteList):
            emoteList.remove(emote)
            emoteDict.update({'emotes': emoteList})
            emoteFile = open("twitchChannel.json", "wt")
            emoteFile.write(json.dumps(emoteDict, indent=2))
            await ctx.send("Emote " + emote + " successfully removed!")
            emoteFile.close()
        else:
            await ctx.send("That emote was not registered to begin with.")
    else:
        await ctx.send("You don't have the permissions to use this command!")
"""

# Sends the channel rules as a chat message
@bot.command(name="rules")
async def rules(ctx):
    msg = "/me Here are the channel rules! "
    try:
        subRuleDict = ExtFuncs.filePath(gid).twitchData.get('Rules')
    except:
        msg = f'No rules could be found for the channel: {channelToJoin[0]}'
        await ctx.send(str(msg))
        return
    if subRuleDict != None or subRuleDict != {}:
        for rule in sorted(subRuleDict.keys()):
            msg = msg + rule + ". " + str(subRuleDict.get(rule)) + " "
    else:
        msg = f'No rules could be found for the channel: {channelToJoin[0]}'
    await ctx.send(str(msg))

# Adds a rule to the rules file


@bot.command(name="addRule")
async def addRule(ctx, *rule):
    rule = str(" ".join(rule[:]))
    filePath = ExtFuncs.filePath(gid)
    with open(filePath.jsonPath, "rt") as ruleDict:
        ruleDict = json.loads(ruleDict.read())
        minorRuleDict = ruleDict.get('TwitchChannel')
        subRuleDict = minorRuleDict.get('Rules')

    if (ctx.author.name.lower() == os.environ["CHANNEL"] or ctx.author.is_mod == True):
        writeRuleFile = open(filePath.jsonPath, 'wt')
        try:
            sortKeys = sorted(subRuleDict.keys())
            newKey = int(sortKeys[-1]) + 1
        except:
            newKey = 1
        subRuleDict.update({str(newKey): rule})
        minorRuleDict.update({'Rules': subRuleDict})
        ruleDict.update({'TwitchChannel': minorRuleDict})
        writeRuleFile.write(json.dumps(ruleDict, indent=2))
        writeRuleFile.close()
        await ctx.send("The rule, " + '"' + str(rule) + '"' + " with the ID of " + str(newKey) + " has been successfully added to the rules list.")
    else:
        await ctx.send("@" + ctx.author.name + " You don't have the permissions to use this command!")


# Removes a rule from the rules file


@bot.command(name="removeRule")
async def removeRule(ctx, ruleNum):
    filePath = ExtFuncs.filePath(gid)
    ruleNum = str(ruleNum)
    with open(filePath.jsonPath, 'rt') as ruleDict:
        ruleDict = json.loads(ruleDict.read())
        minorRuleDict = ruleDict.get('TwitchChannel')
        subRuleDict = minorRuleDict.get('Rules')

    if (ctx.author.name.lower() == os.environ["CHANNEL"] or ctx.author.is_mod == True):
        if (ruleNum in subRuleDict.keys()):
            writeRuleFile = open(filePath.jsonPath, "wt")
            subRuleDict.pop(ruleNum)
            minorRuleDict.update({'Rules': subRuleDict})
            ruleDict.update({'TwitchChannel': minorRuleDict})
            writeRuleFile.write(json.dumps(ruleDict, indent=2))
            await ctx.send("The rule with ID " + ruleNum + " has been successfully removed.")
            writeRuleFile.close()
        else:
            await ctx.send(f'The rule {str(ruleNum)} could not be found in the rule list.')
    else:
        await ctx.send("@" + ctx.author.name + " You don't have the permissions to use this command!")

# Displays a specific rule


@bot.command(name="rule")
async def rule(ctx, num):
    try:
        subRuleDict = ExtFuncs.filePath(gid).twitchData.get('Rules')
    except:
        subRuleDict = None

    if str(num).lower() in subRuleDict.keys():
        await ctx.send("/me " + subRuleDict.get(num))
    else:
        await ctx.send("/me That rule could not be found.")

# A basic text message sent via the chat that will give a summary of recent events in game(Has to be updated manually)


@bot.command(name="whatimiss")
async def whatimiss(ctx):
    msg = ExtFuncs.filePath(gid).twitchData.get('missTxt')
    await ctx.send("@" + ctx.author.name + " While you were gone, " + msg)

# Command for updating the "whatimiss" response message


@bot.command(name="updateMiss")
async def updateMiss(ctx, *txt):
    if(ctx.author.is_mod == True):
        fileData = ExtFuncs.filePath(gid)
        msgData = fileData.jsonData
        twitchStuffs = msgData.get('TwitchChannel')
        twitchStuffs.update({'missTxt': (" ".join(txt[:]))})
        msgData.update({'TwitchChannel': twitchStuffs})
        with open(fileData.jsonPath, 'wt') as writeOut:
            writeOut.write(json.dumps(msgData, indent=2))
        await ctx.send("What did I miss file has been updated successfully.")
    else:
        await ctx.send("You do not have the required permissions to use this command!")

# Custom entry lines
@bot.command(name="addEntry")
async def addEntry(ctx, *txt):
    if(ctx.author.is_mod == True):
        fileData = ExtFuncs.filePath(gid)
        msgData = fileData.jsonData
        twitchStuffs = msgData.get('TwitchChannel')
        entryLines = twitchStuffs.get('entryLines')
        newEntry = str(" ".join(txt[:]))
        print(entryLines)
        entryLines.append(newEntry)
        twitchStuffs.update({'entryLines': entryLines})
        msgData.update({'TwitchChannel': twitchStuffs})
        with open(fileData.jsonPath, 'wt') as writeOut:
            writeOut.write(json.dumps(msgData, indent=2))
        await ctx.send(f"The entry {newEntry} was successfully added.")
    else:
        await ctx.send("You do not have the required permissions to use this command!")

# Death counter!


@bot.command(name="deathCount")
async def deathCount(ctx):
    await ctx.send("The current number of deaths for this stream is " + str(deathCounter))

# Adds a death to the death counter


@bot.command(name="addDeath")
async def addDeath(ctx):
    # Adds a single death to the counter every time the command is run
    global deathCounter
    deathCounter += 1
    await ctx.send("Death counter updated successfully.")

# Resets the death counter to 0


@bot.command(name="resetDeath")
async def resetDeath(ctx):
    if (ctx.author.is_mod == True):
        global deathCounter
        deathCounter = 0
        await ctx.send("Death counter successfully reset.")
    else:
        await ctx.send("You don't have permission to use this command")

# Sets the death counter to a custom number


@bot.command(name="setDeath")
async def setDeath(ctx, num):
    if (ctx.author.is_mod == True):
        global deathCounter
        deathCounter = int(num)
        await ctx.send("Death counter has been set to " + str(deathCounter))
    else:
        await ctx.send("You don't have the permissions to use this command")
"""
# Add a word to the banned word list
@bot.command(name="blacklist")
async def blacklist(ctx, word):
    bannedWords = open("bannedWords.txt", "at")
    if (ctx.author.is_mod == True):
        bannedWords.write("\n" + word)
        await ctx.send("That word has been successfully added to the blacklist")
    else:
        await ctx.send("You don't have permission to use this command")
    bannedWords.clos()
"""

@customChecks.checkMod()
@bot.command(name="so")
async def so(ctx, user):
    user = str(user).lstrip('@')
    await ctx.send(f'You should go checkout {user} over at https://wwww.twitch.tv/{user}')

class customComs:
    def __init__(self, gid):
        self.gid = gid
        self.varFile = ExtFuncs.filePath(gid)
        self.twitchData = self.varFile.twitchData
        self.guildData = self.varFile.jsonData
        self.customComs = self.varFile.twitchData.get('CustomComs')

    def searchComs(self, comToSearch):
        if str(comToSearch) in self.customComs.keys():
            return True
        else:
            return False

    def addCom(self, comName, comResult):
        comResult = ' '.join(comResult[:])
        self.customComs.update({comName: comResult})
        self.twitchData.update({'CustomComs': self.customComs})
        self.guildData.update({'TwitchChannel': self.twitchData})
        with open(self.varFile.jsonPath, 'wt') as writeData:
            writeData.write(json.dumps(self.guildData, indent=2))

    def removeCom(self, comName):
        self.customComs.pop(comName)
        self.twitchData.update({'CustomComs': self.customComs})
        self.guildData.update({'TwitchChannel': self.twitchData})
        with open(self.varFile.jsonPath, 'wt') as writeData:
            writeData.write(json.dumps(self.guildData, indent=2))

@customChecks.checkMod()
@bot.command(name="addCom")
async def addCom(ctx, commandName, *commandReturn):
    guildData = customComs(gid)
    commandName = str(commandName).lstrip('!')
    if guildData.searchComs(commandName):
        await ctx.send(f'The command {commandName} already exists. If you wish to edit it, please use the command "!editCom <Command Name> <New Command Result>"')
        return
    guildData.addCom(commandName, commandReturn)
    await ctx.send(f'The command !{commandName} was successfully added.')

@customChecks.checkMod()
@bot.command(name="editCom")
async def editCom(ctx, commandName, *commandReturn):
    guildData = customComs(gid)
    commandName = str(commandName).lstrip('!')
    if not guildData.searchComs(commandName):
        await ctx.send(f"The command {commandName} doesn't appear to exist. If you wish to add it,"' please use the command "!addCom <Command Name> <New Command Result>"')
        return 
    guildData.addCom(commandName, commandReturn)
    await ctx.send(f'The command !{commandName} was successfully updated.')

@customChecks.checkMod()
@bot.command(name='removeCom')
async def removeCom(ctx, commandName):
    guildData = customComs(gid)
    commandName = str(commandName).lstrip('!')
    if not guildData.searchComs(commandName):
        await ctx.send(f'The command {commandName} could not be found.')
        return
    guildData.removeCom(commandName)
    await ctx.send(f'The command !{commandName} was removed successfully.')

@customChecks.checkMod()
@bot.command(name='enableEggs', aliases=['enableEasterEggs'])
async def enableEggs(ctx):
    channelData = ExtFuncs.filePath(gid)
    jsonData = channelData.jsonData
    twitchData = channelData.twitchData
    twitchData.update({'EasterEggs': True})
    jsonData.update({'TwitchChannel': twitchData})
    with open(channelData.jsonPath, 'wt') as writeData:
        writeData.write(json.dumps(jsonData, indent=2))
    await ctx.send('Easter eggs successfully enabled; Enjoy! :)')
    try:
        bot.load_module('modules.twitchCogs.easterEggs')
        await ctx.send('Easter eggs now running! :D')
    except:
        await ctx.send('Failed to load the easter eggs. Consider restarting the twitch bot from discord by running ".killTwitch" followed by ".runTwitch"')
    return
@customChecks.checkMod()
@bot.command(name='disableEggs', aliases=['disableEasterEggs'])
async def disableEggs(ctx):
    channelData = ExtFuncs.filePath(gid)
    jsonData = channelData.jsonData
    twitchData = channelData.twitchData
    twitchData.update({'EasterEggs': False})
    jsonData.update({'TwitchChannel': twitchData})
    with open(channelData.jsonPath, 'wt') as writeData:
        writeData.write(json.dumps(jsonData, indent=2))
    await ctx.send('Easter eggs now disabled.')
    bot.unload_module('modules.twitchCogs.easterEggs')
    try:
        bot.unload_module('modules.twitchCogs.easterEggs')
        #await ctx.send('Easter eggs have been stopped successfully')
    except:
        #await ctx.send('Failed to unload the easter eggs. Consider restarting the twitch bot from discord by running ".killTwitch" followed by ".runTwitch"')
        pass
    return

def safeShutDown():
    print('called safeShutDown-twitch')
    for threadObj in runningThreads:
        threadObj.join()
        print(f'Safely ended thread: {threadObj.name}')
    checker.queue.close()
    print('closed queue')
    bot._ws.teardown()
    print('properly toredown ws')
    return

# Joins the specified twitch channel
async def joinChannel(channelName):
    print('called joinChannel method')
    try:
        await bot.join_channels(channelName)
    except:
        print('failed to join channel...')
