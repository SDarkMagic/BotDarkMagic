import discord
import json
from discord.ext import commands

class commandHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    # DM's the message sender the bot commands
    @commands.command(name="cmds", aliases=["commands", "help"])
    async def cmds(self, ctx, user=None):
        adminName = ((json.loads((open('adminVars.json', 'rt')).read())).get('DiscordBackend')).get('adminName')
        botCommandFile = open("commands.txt", "rt")
        botCommands = botCommandFile.readlines()
        if (user == None):
            DMuser = ctx.author
        else:
            DMuser = ctx.message.mentions[0]
        msg = "Here are the commands currently available in " + adminName +"'s Server:\n```"
        for line in botCommands:
            if (line == None or line == "\\n"):
                continue
            else:
                line.rstrip("\\n")
                msg = msg + line
        print(DMuser)
        await DMuser.send(msg + "\n```")
        botCommandFile.close()


def setup(bot):
    bot.add_cog(commandHelp(bot))