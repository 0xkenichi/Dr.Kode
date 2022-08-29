import os
import discord
import logging
import pandas as pd
from keepalive import keep_alive
import re

logging.basicConfig(level=logging.INFO)

client = discord.Client()
guild = discord.Guild

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game('_scan help'))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content.startswith('_'):

        cmd = message.content.split()[0].replace("_","")
        if len(message.content.split()) > 1:
            parameters = message.content.split()[1:]

        # Bot Commands

        if cmd == 'scan':

            data = pd.DataFrame(columns=['content', 'time', 'author'])
            

            # Acquiring the channel via the bot command
            if len(message.channel_mentions) > 0:
                channel = message.channel_mentions[0]
            else:
                channel = message.channel

            # Aquiring the number of messages to be scraped via the bot command
            if (len(message.content.split()) > 1 and len(message.channel_mentions) == 0) or len(message.content.split()) > 2:
                for parameter in parameters:
                    if parameter == "help":
                        answer = discord.Embed(title="Command Format",
                                               description="""`_scan <channel> <number_of_messages>`\n\n`<channel>` : **the channel you wish to scan**\n`<number_of_messages>` : **the number of messages you wish to scan**\n\n*The order of the parameters does not matter.*""",
                                               colour=0x1a7794) 
                        await message.channel.send(embed=answer)
                        return
                    elif parameter[0] != "<": # Channels are enveloped by "<>" as strings
                        limit = int(parameter)
            else:
                limit = 999999999
            
            answer = discord.Embed(title="Creating your Link History Dataframe",
                                   description="Please Wait. The data will be sent to you privately once it's finished.",
                                   colour=0x1a7794) 

            await message.channel.send(embed=answer)

            def is_command (message):
                if len(msg.content) == 0:
                    return False
                elif msg.content.split()[0] == '_scan':
                    return True
                else:
                    return False

            async for msg in channel.history(limit=limit + 10000):       
                if msg.author != client.user:                          
                    if not is_command(msg): 
                      #url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
                      #reg = re.compile(url_pattern)
                      #if reg.findall(msg.content): 
                      if 'http' in msg.content: 
                          data = data.append({'content': msg.content,
                                            'time': msg.created_at,
                                            'author': msg.author.name}, ignore_index=True)
                    if len(data) == limit:
                        break
             
            # Turning the pandas dataframe into a .csv file and sending it to the user 

            file_location = f"{str(channel.guild.id) + '_' + str(channel.id)}.csv" # Determining file name and location
            data.to_csv(file_location)

            answer = discord.Embed(title="Here is your .CSV File",
                                   description=f"""It might have taken a while, but here is what you asked for.\n\n`Server` : **{message.guild.name}**\n`Channel` : **{channel.name}**\n`Messages Read` : **{limit}**""",
                                   colour=0x1a7794) 

            await message.author.send(embed=answer)
            await message.author.send(file=discord.File(file_location, filename='data.csv')) # Sending the file
            os.remove(file_location) # Deleting the file

  
keep_alive()
client.run(os.getenv('newtkn'))