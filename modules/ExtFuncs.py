# Extra functions that don't make sense to put in the "bot.py" file
import os
from datetime import datetime
import pathlib
import json
import asyncio
import threading

# Global variables
puncList = [",", ".", "?", "!", "'", '"', "(", ")", "#", "-", "_"]
intList = ["0", '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']
initDate = (datetime.now()).strftime("%Y-%m-%D").replace('/', '-')
varPath = pathlib.Path('Vars')

# A function for stripping punctuation from a string
def puncStrip(strIn):
    for char in puncList:
#        print(char)
#            print("punctuation detected")
        strIn.replace(strIn, '')
#            print(itemFinal)
#            return(itemFinal)
#            print("No punctuation was found")
    itemFinal = strIn
    return(itemFinal)

# Strips non-number parts of a string from a string
def ripNum(string):
    stringOut = string
    for char in string:
#        print(char)
        if (char not in intList):
            stringOut = str(stringOut).replace(char, '')
#            print(stringOut)
        else:
            stringOut = stringOut
            continue
    return(stringOut)

def comSep(strIn):
    strOut = str(strIn) + ', '
    return(str(strOut))

def log(logPath, logName, author, channel, message):
    time = datetime.now()
    log = pathlib.Path(logPath / logName)
    log = log.resolve()
    if (log.exists() == True):
        logFile = open(log, 'at', encoding='utf-8')
        logFile.write(comSep(time) + comSep(author) + comSep(channel) + message + '\n')
    else:
        logFile = open(log, 'wt', encoding='utf-8')
        logFile.write('Time, Author, Channel, Message\n' + comSep(time) + comSep(author) + comSep(channel) + message + '\n')
    logFile.close()
"""
def getLog():
    global fileName
    return(fileName)
"""

def floatList(num):
    numList = []
    for n in num:
        numList.append(float(n))
    return(numList)

# Opens and reads data from a server's variable data. returns a dict of the data.
def readVars(guildID):
    guildID = str(guildID)
    varDir = pathlib.Path(varPath / guildID)
    openFile = open(f'{varDir / guildID}.json', 'rt')
    dataOut = json.loads(openFile.read())
    openFile.close()
    return(dataOut)
    
class filePath:
    def __init__(self, guildID):
        self.jsonPath = pathlib.Path(f'Vars/{guildID}/{guildID}.json')
        self.genPath = pathlib.Path(f'Vars/{guildID}')
        self.twitchData = self.findGuildData('TwitchChannel')
        self.bannedWords = self.findGuildData('BannedWords')
        self.jsonData = self.readGuildJson()


    def findGuildData(self, dataIn):
        with open(self.jsonPath, 'rt') as openFile:
            dataOut = json.loads(openFile.read()).get(dataIn)
        return dataOut

    def readGuildJson(self):
        with open(self.jsonPath, 'rt') as readData:
            dataOut = json.loads(readData.read())
        return dataOut

class globalVars:
    def __init__(self):
        self.globalVars = self.getGlobalVars()
        self.streamers = self.globalVars.get('TwitchChannel')

    def getGlobalVars(self):
        with open(pathlib.Path(f'Vars/globalVars.json'), 'rt') as readVars:
            varData = json.loads(readVars.read())
            return(varData)
