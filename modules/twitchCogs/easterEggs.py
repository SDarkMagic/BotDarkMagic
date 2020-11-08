import twitchio
from twitchio.ext import commands

@commands.cog()
class eggs():
    def __init__(self, bot):
        self.bot = bot
        print('started eastereggs cog')

def setup(bot):
    bot.add_cog(eggs(bot))