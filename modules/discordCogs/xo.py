import numpy as np
import discord
from discord.ext import commands
import random

class xoGame(commands.Cog):

    inGame = False
    board = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    coordList = ['a1', 'a2', 'a3', 'b1', 'b2', 'b3', 'c1', 'c2', 'c3']
    arrayRelateDict = {
        'a1':[0,0],
        'a2':[0,1],
        'a3':[0,2],
        'b1':[1,0],
        'b2':[1,1],
        'b3':[1,2],
        'c1':[2,0],
        'c2':[2,1],
        'c3':[2,2]
    }

    def __init__(self, bot):
        self.bot = bot

    # Generates the embed for the game
    def embedGen(self, title, board):
        #stuff here
        print('yes')

    def gameStart(self):
        #board = self.board
        self.board = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    # Has the computer decide where to go at random
    def comTurn(self):
        board = self.board
#        print(board)
        rowChoice = random.choice(list(range(0,3)))
        columnChoice = random.choice(list(range(0,3)))
        continueCycle = True
#        random.choice([0, 1])
#        print(board[comChoice])
        while continueCycle == True:
            print([rowChoice, columnChoice])
            if ((board[rowChoice,columnChoice]) == 0):
                board[rowChoice,columnChoice] = 1
                continueCycle = False
            else:
                rowChoice = random.choice(list(range(0,3)))
                columnChoice = random.choice(list(range(0,3)))
                continue
        print(board)

    def checkWin(self):
        board = self.board
        winner = None
        index = 0

        boardCount = [
        np.count_nonzero(board == 1, axis=0),
        np.count_nonzero(board == 2, axis=0),
        np.count_nonzero(board == 1, axis=1),
        np.count_nonzero(board == 2, axis=1)
        ]

        def checkMatch(self, listIn):
            for x in listIn:
                if int(x) == int(3):
                    print('Winner!')
                    return(True)
                else:
                    return(False)

        for item in boardCount:
            win = checkMatch(self, item)
            if (win == True):
                if (boardCount.index(index) == boardCount[1] or boardCount.index(index) == boardCount[3]):
                    winner = 'Computer'
                elif (boardCount.index(index) == boardCount[0] or boardCount.index(index) == boardCount[2]):
                    winner = 'Player'
                else:
                    winner = 'unknown'
                index += 1
            else:
                continue
        print(winner)
                
            



    @commands.command(name='xo')
    async def xo(self, ctx):
        if self.inGame == True:
            await ctx.send('no.')
        else:
            await ctx.send('Here is the fabled snake!')
            self.inGame = True
            xoGame.gameStart(self)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if self.inGame == True:
            if ctx.author == self.bot.user:
                return
            elif self.inGame == False:
                return
            else:
                if str(ctx.content).lower() in self.coordList:
                    coords = self.arrayRelateDict.get((ctx.content).lower())
                    if self.board[coords[0], coords[-1]] == 0:
                        self.board[coords[0], coords[-1]] = 2
                        xoGame.checkWin(self)
                        self.comTurn()
                        xoGame.checkWin(self)
                    else:
                        await ctx.channel.send(f'The spot {ctx.content} is already occupied. Please choose a different spot.')
                else:
                    await ctx.channel.send(f'The spot {ctx.content} could not be found. Try again with a spot that is actually on the board.')
#            await self.bot.process_commands(ctx)
#        print(ctx)

    @commands.command(name='exit', aliases=['exitGame', 'quitXO'])
    async def exit(self, ctx):
        self.inGame = False
        await ctx.send('Exiting!')
        return()





def setup(bot):
    bot.add_cog(xoGame(bot))