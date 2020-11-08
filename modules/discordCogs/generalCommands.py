import discord
import json
import pathlib
from discord.ext import commands
from .. import ExtFuncs

class generalCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='avatar')
    async def avatar(self, ctx, user=None):
        if user == None:
            user = self.bot.get_user(ctx.author.id)
        else:
            user = self.bot.get_user(int((str(user).lstrip('<@!')).rstrip('>')))
            print(user)
        await ctx.send(f'https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}?size=2048')

    # Sends all of the server emotes as a chat message
    @commands.command("emotes")
    async def emotes(self, ctx):
        guildID = ctx.guild.id
        guildObj = self.bot.get_guild(guildID)
        msg = "Emotes available on this server are: "
        emotes = guildObj.emojis
        for emote in emotes:
            msg = msg + str(emote)
        await ctx.send(msg)

    # Googles something based on user input
    @commands.command("google")
    async def google(self, ctx, *query):
    #  Syntax for using the query ".join(rule[:])"
        searchLink = "https://lmgtfy.com/?q="
        searchStr = " ".join(query[:])
        searchList = []
        print(searchStr)
        iterCount = 0

        
        for word in searchStr.split():
            searchList.append(word)
        print(searchList)

        for item in searchList:
            if iterCount + 1 != len(searchList):
                searchLink = searchLink + item + "+"
                iterCount += 1
            else:
                searchLink = "<" + searchLink + item + "+" + ">"
        await ctx.send(searchLink)

    # Sends the simple message of 'it is what it is'
    @commands.command(name="iwi")
    async def iwi(self, ctx):
        await ctx.send("It is what it is... ")

    # Sends a message saying "Not right now"
    @commands.command(name="nrn")
    async def nrn(self, ctx):
        await ctx.send("Not right now.")

    # Roles
    @commands.command(name='serverRoles')
    async def serverRoles(self, ctx):
        global rolesVar
        rolesVar = ctx.guild.roles
        print(rolesVar)
        await ctx.send(content=str(rolesVar[-1]))

    # Adds Numbers
    @commands.command(name='add')
    async def add(self, ctx, *num):
        numList = ExtFuncs.floatList(num)
        numAdd = numList[0]
        del numList[0]
        for x in numList:
            numAdd = float(numAdd) + x
        await ctx.send(numAdd)

    # Subtracts Numbers
    @commands.command(name='subtract')
    async def subtract(self, ctx, *num):
        numList = ExtFuncs.floatList(num)
        numSub = numList[0]
        del numList[0]
        for x in numList:
            numSub = float(numSub) - x
        await ctx.send(numSub)

    # multiplies Numbers
    @commands.command(name='multiply')
    async def multiply(self, ctx, *num):
        numList = ExtFuncs.floatList(num)
        numMul = numList[0]
        del numList[0]
        for x in numList:
            numMul = float(numMul) * x
        await ctx.send(numMul)

    # Divides Numbers
    @commands.command(name='divide')
    async def divide(self, ctx, *num):
        numList = ExtFuncs.floatList(num)
        numDiv = numList[0]
        del numList[0]
        for x in numList:
            numDiv = float(numDiv) / x
        await ctx.send(numDiv)

    # Converts a Celcius temperature to a Farenheight temperature
    @commands.command(name="celToFar", aliases=['convertCel'])
    async def celToFar(self, ctx, temperature):
        string = ExtFuncs.ripNum(temperature)
        farFromCel = float(string) * 1.8 + 32
        await ctx.send(str(farFromCel) + '°F')

    # Converts a Celcius temperature to a Farenheight temperature
    @commands.command(name="farToCel", aliases=['convertFar'])
    async def farToCel(self, ctx, temperature):
        string = ExtFuncs.ripNum(temperature)
        farFromCel = (float(string) - 32) / 1.8
        await ctx.send(str(farFromCel) + '°C')

def setup(bot):
    bot.add_cog(generalCommands(bot))