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

initChannels = ['BotDarkMagic']
runningThreads = []

class dataChecker:
    def __init__(self, data):
        self.queue = data

    async def checkLoop(self):
        checkData = self.getPutData()
        try:
            checkGuild = checkData.get(gid)
            checkAll = checkData.get('all')
        except:
            checkGuild = None
            checkAll = None
        print('a')
        if checkGuild == True or checkAll == True:
            bot.part_channels(channelToJoin)
        else:
            await asyncio.sleep(30)
            await self.checkLoop()

    def getPutData(self):
        dataDown = self.queue.get()
        self.queue.put(dataDown)
        print(dataDown)
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
    checker = dataChecker(data)
    asyncio.gather(
        checker.checkLoop()
#        bot.run()
    )


bot = commands.Bot(
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=initChannels
    )

# Global Variables
now = time.strftime("%Y-%m-%d_%H%M%S")
nameColors = ["Blue", "BlueViolet", "CadetBlue", "Chocolate", "Coral", "DodgerBlue", "Firebrick", "GoldenRod", "Green", "HotPink", "OrangeRed", "Red", "SeaGreen", "SpringGreen", "YellowGreen"]
ytLink = "https://www.youtube.com/channel/UCg5GCfIEYGScRsbss8lhH7A?"
cmdLink = "https://docs.google.com/document/d/1Stt8MMKHmD1Nj2BOc_Pg8s6i5u2CMByu8-sib89x06Q/edit?usp=sharing"
me = "/me "
deathCounter = 0
deathCountFile = open("deathCount.txt", "wt")
# initiate the logging and death count files
deathCountFile.write("Death counter: " + str(deathCounter))
deathCountFile.close()
gid = None

# Bot Events

@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f"{os.environ['BOT_NICK']} is now online!")
    await joinChannel(channelToJoin)
    await bot.part_channels(initChannels)
    varData = ExtFuncs.filePath(gid).twitchData
    try:
        randomEntrance = random.choice(varData.get('entryLines'))
    except:
        randomEntrance = f'No custom entrance lines for the bot were found. To add some, please use the command "!addEntry <text for bot to say when joining the chat>"'
    bot.load_module('modules.twitchCogs.easterEggs')
    print(randomEntrance)
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(channelToJoin[0], f"/me {randomEntrance}")

@bot.event
async def event_message(ctx):
    'Runs every time a message is sent in chat.'
    # make sure the bot ignores it and the streamer
    if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
#        await event_log(ctx)
        return
    else:
        await bot.handle_commands(ctx)
        await event_filter(ctx)
        await magic(ctx)
#        await event_log(ctx)

# Chat filter
async def event_filter(ctx):
    # A function to read every message and moderate based off of a predetermined list of words
    bannedWordsList = ExtFuncs.filePath(gid).bannedWords
    for listObj in bannedWordsList:
        listObjIndex = bannedWordsList.index(listObj)
        listObj = listObj.rstrip("\n")
        bannedWordsList[listObjIndex] = listObj

#    print(bannedWordsList)
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
# Magic
async def magic(ctx):
    """A really stupid function whose sole purpose is to correct anyone who says 'magic' with 'dark magic'"""
    msgToList = ctx.content.split(" ")
    for word in msgToList:
        if (word.lower() == "magic"):
            await ctx.channel.send("@" + ctx.author.name + " *Dark magic")
            break
        else:
            continue

# Runs whenever there is a subscription
@bot.event
async def event_usernotice_subscription(ctx):
    print(ctx)


# Bot Commands


# Changes the bot's name color to a randomly selected one
@bot.command(name="color")
async def color(ctx):
    formatHex = random.choice(nameColors)
    print(formatHex)
    await bot._ws.send_privmsg(channelToJoin[0], f"/color " + formatHex)

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

@bot.command(name="discord")
async def discord(ctx):
    await ctx.send(me + "@" + ctx.author.name + " Come join the discord and hangout even after the stream by going to " + ExtFuncs.filePath(gid).findGuildData('DiscordBackend').get())

# Sends a link to the youtube channel as a chat message


@bot.command(name="youtube")
async def youtube(ctx):
    await ctx.send(me + "@" + ctx.author.name + " Subscribe to my YouTube channel at " + ytLink)
"""

# Sends the channel rules as a chat message


@bot.command(name="rules")
async def rules(ctx):
    msg = "/me Here are the channel rules! "
    subRuleDict = ExtFuncs.filePath(gid).twitchData.get('Rules')

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
        ruleDict = ruleDict
        subRuleDict = ruleDict.get('rules')
    writeRuleFile = open(filePath.jsonPath, 'wt')

    if (ctx.author.name.lower() == os.environ["CHANNEL"] or ctx.author.is_mod == True):
        sortKeys = sorted(subRuleDict.keys())
        try:
            newKey = int(sortKeys[-1]) + 1
        except:
            newKey = 1
        subRuleDict.update({str(newKey): rule})
        ruleDict.update({'rules': subRuleDict})
        writeRuleFile.write(json.dumps(ruleDict, indent=2))
        await ctx.send("The rule, " + '"' + str(rule) + '"' + " with the ID of " + str(newKey) + " has been successfully added to the rules list.")
    else:
        await ctx.send("@" + ctx.author.name + " You don't have the permissions to use this command!")
    writeRuleFile.close()

# Removes a rule from the rules file


@bot.command(name="removeRule")
async def removeRule(ctx, ruleNum):
    filePath = ExtFuncs.filePath(gid)
    with open(filePath.jsonPath, 'rt') as ruleDict:
        ruleDict = ruleDict
        subRuleDict = ruleDict.get('rules')

    if (ctx.author.name.lower() == os.environ["CHANNEL"] or ctx.author.is_mod == True):
        if (ruleNum in subRuleDict.keys()):
            writeRuleFile = open(filePath.jsonPath, "wt")
            subRuleDict.pop(ruleNum)
            ruleDict.update({'rules': subRuleDict})
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
    subRuleDict = ExtFuncs.filePath(gid).twitchData.get('Rules')

    if str(num).lower() in subRuleDict.keys():
        await ctx.send("/me " + subRuleDict.get(num))
    else:
        await ctx.send("/me That rule could not be found.")

# A basic text message sent via the chat that will give a summary of recent events in game(Has to be updated manually)


@bot.command(name="whatimiss")
async def whatimiss(ctx):
    msgFile = open("whatimiss.txt", "rt")
    msg = msgFile.read()
    await ctx.send("@" + ctx.author.name + " While you were gone, " + msg)

# Command for updating the "whatimiss" response message


@bot.command(name="updateMiss")
async def updateMiss(ctx, *txt):
    if(ctx.author.is_mod == True):
        msgFile = open("whatimiss.txt", "wt")
        print("The sender has the permissions to use this command")
        msgFile.write(" ".join(txt[:]))
        await ctx.send("What did I miss file has been updated successfully.")
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
    deathCountFile = open("deathCount.txt", "wt")
    global deathCounter
    deathCounter += 1
    deathCountFile.write("Death counter: " + str(deathCounter))
    await ctx.send("Death counter updated successfully.")
    deathCountFile.close()

# Resets the death counter to 0


@bot.command(name="resetDeath")
async def resetDeath(ctx):
    if (ctx.author.is_mod == True):
        deathCountFile = open("deathCount.txt", "wt")
        global deathCounter
        deathCounter = 0
        deathCountFile.write("Death counter: " + str(deathCounter))
        await ctx.send("Death counter successfully reset.")
        deathCountFile.close()
    else:
        await ctx.send("You don't have permission to use this command")

# Sets the death counter to a custom number


@bot.command(name="setDeath")
async def setDeath(ctx, num):
    if (ctx.author.is_mod == True):
        global deathCounter
        deathCountFile = open("deathCount.txt", "wt")
        deathCounter = int(num)
        deathCountFile.write("Death counter: " + str(deathCounter))
        await ctx.send("Death counter has been set to " + str(deathCounter))
        deathCountFile.close()
    else:
        await ctx.send("You don't have the permissions to use this command")

# Add a word to the banned word list


@bot.command(name="blacklist")
async def addBlacklist(ctx, word):
    bannedWords = open("bannedWords.txt", "at")
    if (ctx.author.is_mod == True):
        bannedWords.write("\n" + word)
        await ctx.send("That word has been successfully added to the blacklist")
    else:
        await ctx.send("You don't have permission to use this command")
    bannedWords.clos()

# Stupid chat message


@bot.command(name="good")
async def good(ctx):
    await ctx.send("I swear I'm actually really good at this game!")


@bot.command(name="so")
async def so(ctx, user):
    user = str(user).lstrip('@')
    await ctx.send(f'You should go checkout {user} over at https://wwww.twitch.tv/{user}')


@bot.command(name="exit")
async def exit(ctx):
    print(ctx.author.name.lower)
    if (ctx.author.name.lower() == os.environ["CHANNEL"].lower()):
        await ctx.send('shutting down!')
        await bot.part_channels(channelToJoin)
#        await bot.kill()
        sys.exit()
    else:
        await ctx.send("You don't appear to own this channel...")
"""
@bot.command(name='clip')
async def clip(ctx):
    await bot.create_clip(os.environ['TMI_TOKEN'])
"""

# Joins the specified twitch channel
async def joinChannel(channelName):
    print('called joinChannel method')
    try:
        await bot.join_channels(channelName)
    except:
        print('failed to join channel...')



#if __name__ == '__main__':
#    run()
