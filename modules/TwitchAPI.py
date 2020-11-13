# Functions for dealing with the absolute mess that is the Twitch API
import requests
import time
import json
import os
import discord
import pathlib
import twitchio

oauthKey = None
#adminVarFile = open('adminVars.json', 'rt')
#adminVars = json.load(adminVarFile)
#links = adminVars.get('Links')
#dcBackend = adminVars.get('DiscordBackend')
oauthDict = {}

# Requests an oauth token from the Twitch API
def getAccessToken():
    global oauthDict
    OAUTH_REQUEST_ENDPOINT = 'https://id.twitch.tv/oauth2/token'
    REQUEST_HEADERS = {
        'client_id' : os.getenv('TWITCH_CLIENT_ID'),
        'client_secret' : os.getenv('TWITCH_CLIENT_SECRET'),
        'grant_type' : 'client_credentials'
    }
    oauth = requests.post(url=OAUTH_REQUEST_ENDPOINT, params=REQUEST_HEADERS)
    oauthDict = oauth.json()
    oauthKey = oauthDict.get('access_token')
    return oauthKey

# Checks Twitch API to see if stream is live
def checkUser(user): #returns true if online, false if not
    autho = "Bearer " + str(oauthKey)
    jsonDict = {}
    API_HEADERS = {
    'Client-ID' : os.getenv('TWITCH_CLIENT_ID'),
    'Authorization' : autho
}   
    def request(user, headers):
        try:
            status = requests.get('https://api.twitch.tv/helix/streams?user_login=' + user, headers=API_HEADERS)
            return status
        except requests.exceptions.ConnectionError:
            time.sleep(60)
            request(user, headers)

    status = request(user, API_HEADERS)
    jsondata = status.json().get('data')
    for obj in jsondata:
        if (obj != None):
            jsonDict.update(obj)
        else:
            continue
    try:
        print(jsondata)
        if jsonDict.get("type") == "live":
            return True
        else:
            return False
    except Exception as e:
        print("Error checking user: ", e)
        return False    

# Generates the new Oauth token
def getOauth():
    global oauthKey
    oauthKey = getAccessToken()

def generateEmbed(user):
    jsonDict = {}
    autho = "Bearer " + str(oauthKey)
    adminName = str(user)
    API_HEADERS = {
    'Client-ID' : os.getenv('TWITCH_CLIENT_ID'),
    'Authorization' : autho
    }
    status = requests.get('https://api.twitch.tv/helix/streams?user_login=' + user, headers=API_HEADERS)
    jsondata = status.json().get('data')
    for obj in jsondata:
        if (obj != None):
            jsonDict.update(obj)
        else:
            continue
    with open(pathlib.Path('gameIdDatabase.json'), 'rt') as gameDatabaseFile:
        gameDatabase = json.loads(gameDatabaseFile.read())
        gameInfo = gameDatabase.get(jsonDict.get('game_id'))
    if (gameInfo is not None):
        gameInfo = gameInfo
    else:
        try:
            gameInfo = getGames(jsonDict.get('game_id'))
        except:
            gameInfo = 'Unknown Game'
    streamEmbed = discord.Embed(
        title= adminName + ' Just Went Live!',
        description=jsonDict.get('title'),
        color=discord.Color(0xB345E2),
        url=str(f'https://www.twitch.tv/{user}')
    )
    streamEmbed.set_image(url='https://static-cdn.jtvnw.net/previews-ttv/live_user_' + user.lower() + '.jpg')
    streamEmbed.set_thumbnail(url=gameInfo[-1])
    streamEmbed.add_field(name='Game', value=gameInfo[0], inline=True)
    return streamEmbed

def getGames(game_id):
    autho = "Bearer " + str(oauthKey)
    API_HEADERS = {
        'Client-ID' : os.getenv('TWITCH_CLIENT_ID'),
        'Authorization' : autho
        }
    gameRequest = requests.get(f'https://api.twitch.tv/helix/games?id={game_id}', headers=API_HEADERS)
    gameData = gameRequest.json().get('data')[0]
    gameName = [gameData.get('name'), (str(gameData.get('box_art_url')).rstrip("-{width}x{height}.jpg") + '.jpg')]
    with open(pathlib.Path('gameIdDatabase.json'), 'rt') as readGameDB:
        dataBase = json.loads(readGameDB.read())
    if game_id in dataBase.keys():
        return gameName
    else:
        dataBase.update({game_id: gameName})
        with open(pathlib.Path('gameIdDatabase.json'), 'wt') as writeGameDB:
            writeGameDB.write(json.dumps(dataBase, indent=2))
    return gameName

def authTimeLimit():
    timeLeft = oauthDict.get('expires_in')
    return(int(timeLeft))