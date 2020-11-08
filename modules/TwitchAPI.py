# Functions for dealing with the absolute mess that is the Twitch API
import requests
import time
import json
import os
import discord
import twitchio

oauthKey = None
#adminVarFile = open('adminVars.json', 'rt')
#adminVars = json.load(adminVarFile)
#links = adminVars.get('Links')
#dcBackend = adminVars.get('DiscordBackend')
gameDatabase = json.load(open('gameIdDatabase.json', 'rt'))
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
    gameInfo = gameDatabase.get(jsonDict.get('game_id'))
    if (gameInfo is not None):
        gameInfo = gameInfo
    else:
        gameInfo = 'Unknown Game'
    streamEmbed = discord.Embed(
        title= adminName + ' Just Went Live!',
        description=jsonDict.get('title'),
        color=discord.Color(0xB345E2),
        url=str(f'https://www.twitch.tv/{user}')
    )
    streamEmbed.set_image(url='https://static-cdn.jtvnw.net/previews-ttv/live_user_' + user + '.jpg')
    streamEmbed.set_thumbnail(url=os.getenv('TWITCHPFP'))
    streamEmbed.add_field(name='Game', value=gameInfo, inline=True)
    return streamEmbed

def getGames():
    return

def authTimeLimit():
    timeLeft = oauthDict.get('expires_in')
    return(int(timeLeft))