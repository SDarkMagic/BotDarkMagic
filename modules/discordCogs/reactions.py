import discord
import json
from discord.ext import commands
import modules.checks as customChecks

class reactionBase(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
#        print('Loaded "reactionBase" cog!')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, ctx):
        if ctx.member == self.bot.user:
            print('Reaction was added by the bot.')
            return
        else:
            roleReactDict = json.loads(open('messageRoleReactions.json', 'rt').read())
            reactedMessage = str(ctx.message_id)
#            print(reactedMessage)
            if reactedMessage in roleReactDict.keys():
                messageSelect = roleReactDict.get(reactedMessage)
#                print('msg was in the dict')
                if str(ctx.emoji) in messageSelect.keys():
                    userRoles = ctx.member.roles
                    roleToAdd = ctx.member.guild.get_role(int(messageSelect.get(str(ctx.emoji))))
#                    print(userRoles)
#                    print(roleToAdd)
                    userRoles.append(roleToAdd)
                    await ctx.member.edit(roles=userRoles)
                else:
                    print('no')
            elif reactedMessage in (roleReactDict.get('rules')).keys():
                ruleReactions = (roleReactDict.get('rules'))
                messageSelect = ruleReactions.get(reactedMessage)
                if str(ctx.emoji) in messageSelect.keys():
                    userRoles = ctx.member.roles
                    roleToRemove = ctx.member.guild.get_role(int(messageSelect.get(str(ctx.emoji))))
                    userRoles.remove(roleToRemove)
                    await ctx.member.edit(roles=userRoles)
                else:
                    print('no')
            else:
                print('nope')

    @commands.command(name='react')
    async def react(self, ctx):
        await ctx.message.add_reaction(emoji='<:darkStop:711663322990116874>')
    
    # Creates a poll with a yes or no answer
    @commands.command(name='poll01', aliases=['createPoll01', 'cp01'])
    async def poll01(self, ctx, *pollData):
        pollMsg = " ".join(pollData[:])
        await ctx.message.delete()
        await ctx.channel.send(str(f'{pollMsg}\n✅ for yes\n❎ for no'))
        lastMsg = ctx.channel.last_message_id
        msgToAdd = await ctx.channel.fetch_message(lastMsg)
        await msgToAdd.add_reaction(emoji='✅')
        await msgToAdd.add_reaction(emoji='❎')

    # Creates a poll with custom choices
    @commands.command(name='customPoll', aliases=['ccp', 'createCustomPoll'])
    @customChecks.checkRole('Moderators')
    async def customPoll(self, ctx, baseMsg, *optionList):
        tupList = list(optionList)
        optionDict = {}
        print(tupList)
        emoteKey = None
        descValue = None
        
        for item in tupList:
            item.replace('-', ' ')
            itemIndex = tupList.index(item)
            if (int(itemIndex) % 2 == 0):
                emoteKey = str(tupList[int(itemIndex)])
            elif (int(itemIndex) % 2 != 0):
                descValue = str(tupList[int(itemIndex)])
            else:
                print('how did we get here?')
#            print(f'{emoteKey} {descValue}')
            if (emoteKey != None and descValue != None):
                optionDict.update({emoteKey: descValue})
                emoteKey = None
                descValue = None
            else:
                continue

        pollMsg = str(baseMsg.replace('-', ' '))
        await ctx.message.delete()
        print(optionDict)
        for key in optionDict.keys():
#            print('a')
            pollMsg = str(f'{pollMsg}\n{key} - {str(optionDict.get(key)).replace("-", " ")}')
        await ctx.channel.send(pollMsg)
        lastMsg = ctx.channel.last_message_id
        msgToAdd = await ctx.channel.fetch_message(lastMsg)
        for key in optionDict.keys():
            await msgToAdd.add_reaction(emoji=key)


    # Adds a reaction to a message and then stores the data in a file with the associated role
    @commands.command(name='addRoleReact', aliases=['arr', 'roleReact'])
    @customChecks.checkRole('Moderators')
    async def addRoleReact(self, ctx, messageID, reaction, role):
        dictStoreFileRead = open('messageRoleReactions.json', 'rt')
        messageReactRoleDict = json.loads(dictStoreFileRead.read())
        dictStoreFileRead.close()
        dictStoreFileWrite = open('messageRoleReactions.json', 'wt')
        role = (str(role).lstrip('<@&')).rstrip('>')
        print(str(ctx))

        for channel in self.bot.get_all_channels():
#            print(channel)
            try:
                if await channel.fetch_message(int(messageID)) != None:
                    msgToReact = await channel.fetch_message(int(messageID))
                else:
                    continue
            except:
                continue
#        msgToReact = await ctx.fetch_message(int(messageID))
        await msgToReact.add_reaction(reaction)
#        print(role)
        if messageID in messageReactRoleDict.keys():
            subDict = messageReactRoleDict.get(messageID)
            subDict.update({reaction: role})
            messageReactRoleDict.update({messageID: subDict})
        else:
            messageReactRoleDict.update({messageID: {reaction: role}})
        dictStoreFileWrite.write(json.dumps(messageReactRoleDict, indent=2))
        dictStoreFileWrite.close()

    @commands.command(name='addRuleConfirm', aliases=['arc'])
    @customChecks.checkRole('Moderators')
    async def addRuleConfirm(self, ctx, messageID, reaction, roleToRemove):
        dictStoreFileRead = open('messageRoleReactions.json', 'rt')
        messageReactRuleDict = json.loads(dictStoreFileRead.read())
        messageReactRoleDict = messageReactRuleDict.get('rules')
        if messageReactRoleDict != None:
            print('Found rules section.')
        else:
            messageReactRuleDict.update({'rules': {}})
            messageReactRoleDict = messageReactRuleDict.get('rules')

        print(messageReactRoleDict)
        print(messageReactRuleDict)

        dictStoreFileRead.close()
        dictStoreFileWrite = open('messageRoleReactions.json', 'wt')
        role = (str(roleToRemove).lstrip('<@&')).rstrip('>')

        for channel in self.bot.get_all_channels():
#            print(channel)
            try:
                if await channel.fetch_message(int(messageID)) != None:
                    msgToReact = await channel.fetch_message(int(messageID))
                    break
                else:
                    continue
            except:
#                print('invalid channel')
                continue
        
        await msgToReact.add_reaction(reaction)

        messageReactRoleDict.update({messageID: {reaction: role}})
        messageReactRuleDict.update({'rules': messageReactRoleDict})
        dictStoreFileWrite.write(json.dumps(messageReactRuleDict, indent=2))
        dictStoreFileWrite.close()

def setup(bot):
    bot.add_cog(reactionBase(bot))