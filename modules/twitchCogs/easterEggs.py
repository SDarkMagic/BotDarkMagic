import twitchio
import os
import random
from twitchio.ext import commands

@commands.cog()
class eggs():
    def __init__(self, bot):
        self.bot = bot

    async def event_message(self, ctx):
        if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
            return
        else:
            await self.magic(ctx)
    # Magic
    async def magic(self, ctx):
        """A really stupid function whose sole purpose is to correct anyone who says 'magic' with 'dark magic'"""
        msgToList = ctx.content.split(" ")
        for word in msgToList:
            if (word.lower() == "magic"):
                await ctx.channel.send("@" + ctx.author.name + " *Dark magic")
                break
            else:
                continue

    @commands.command(name="good")
    async def good(self, ctx):
        await ctx.send("I swear I'm actually really good at this game!")

    # Changes the bot's name color to a randomly selected one
    @commands.command(name="color")
    async def color(self, ctx):
        nameColors = ["Blue", "BlueViolet", "CadetBlue", "Chocolate", "Coral", "DodgerBlue", "Firebrick", "GoldenRod", "Green", "HotPink", "OrangeRed", "Red", "SeaGreen", "SpringGreen", "YellowGreen"]
        formatHex = random.choice(nameColors)
        await self.bot._ws.send_privmsg(ctx.channel, f"/color " + formatHex)


def setup(bot):
    bot.add_cog(eggs(bot))