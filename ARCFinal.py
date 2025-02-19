import discord 
from discord import Intents, app_commands, InteractionMessage, InteractionResponse
import asyncio
from discord.ext import tasks
from discord.ext.commands import BucketType, Cog, command, cooldown, has_permissions
import sqlite3
from aiohttp import ClientSession, TCPConnector
import discord.utils
import random
from discord.ext import commands
import logging
from os import path
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
from collections import defaultdict
import shlex
import string
import traceback
import re
from discord.app_commands import Choice
from psnawp_api import PSNAWP
import string
import time
from interactions import Button, SelectMenu, SelectOption
import aiofiles
import concurrent.futures
from functools import partial
import typing
import datetime 
from datetime import timezone 

red = 0xe74c3c
black = 0x546e7a
black1 = 2303786
green = 0x2ecc71
yellow = 0xf1c40f
db_file = "freewlbot.db" #HARD CODED BOT FILE
discords = []


TOKEN = ("YOUR TOKEN") #BOT TOKEN

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True  

client = commands.Bot(command_prefix="!", intents=intents)


async def some_command_function(interaction):
    output = await aids(interaction)


async def aids(interaction:discord.Interaction):
              with sqlite3.connect("freewlbot.db") as main:
                   cursor = main.cursor()
                   cursor.execute(f"SELECT ntoken FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
                   nitoken = cursor.fetchone()   
                   nitoken = nitoken[0]
                   header = {"Authorization": f"Bearer {nitoken}"}
                   cursor.close()
                   print (header)
                   return header
              
            

@client.tree.command(name="setup")
@app_commands.checks.has_permissions(administrator=True)
@discord.app_commands.checks.cooldown(1, 900.0)
async def setup(interaction: discord.Interaction, clustername: str, nitradotoken: str, freewlmapid: str, wlchannelmention: str, channelforstatus: str):
    with sqlite3.connect("freewlbot.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT ntoken FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
        data = cursor.fetchall()
        print(data)

    print("Has Permissions")

    if data:
        cursor.execute(
            "UPDATE clusterinfo SET ntoken = ?, clustername = ?, freewlmap = ?, freewlchannel = ?, statuschannel = ? WHERE guild_id = ?",
            (nitradotoken, clustername, freewlmapid, wlchannelmention, channelforstatus, interaction.guild.id)
        )

        embed2 = discord.Embed(title="Successfully Updated All Info, Please Ensure All Bot Integrations Are Setup In Discord Settings Correctly.")
        await interaction.response.send_message(embed=embed2, ephemeral=True)
        db.commit()
    else:
        cursor.execute(
            "INSERT INTO clusterinfo (ntoken, guild_id, freewlmap, clustername, freewlchannel, statuschannel) VALUES (?, ?, ?, ?, ?, ?)",
            (nitradotoken, interaction.guild.id, freewlmapid, clustername, wlchannelmention, channelforstatus)
        )
        db.commit()
        embed3 = discord.Embed(description="Successfully Added All Info, Please Ensure All Bot Integrations Are Setup In Discord Settings Correctly.")
        await interaction.response.send_message(embed=embed3, ephemeral=True)

    url1 = "https://api.nitrado.net/services"
    a = await aids(interaction)
    async with ClientSession() as session:
        async with session.get(url1, headers=a) as response:
            response = await response.json()
            res = response["data"]["services"]
            service_list = []
            for services in res:
                service_list.append(services["id"])
            contexts = str(service_list)
            string_without_brackets = re.sub(r"[\[\]]", '', contexts)
            cursor.execute("UPDATE clusterinfo SET services = ? WHERE guild_id = ? AND (SELECT changes() > 0)", (string_without_brackets, interaction.guild.id))
            if cursor.rowcount == 0:
                cursor.execute("INSERT INTO clusterinfo (services, guild_id) VALUES (?, ?)", (string_without_brackets, interaction.guild.id))
            db.commit()

    cursor.close()


@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You need the Administrator role to use this command.", ephemeral=True)
    else:
        print(f"An error occurred: {error}")
        await interaction.response.send_message("An error occurred while processing your command.", ephemeral=True)

@client.tree.command(name="serverinfo")
async def xun(interaction: discord.Interaction):
     with sqlite3.connect("freewlbot.db") as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT clustername FROM clusterinfo WHERE guild_id = {interaction.guild.id}")
        namea = cursor.fetchone()
        name1 = namea[0]
        url1 = ("http://arkdedicated.com/ps4/cache/unofficialserverlist.json")
        async with ClientSession() as session:
                async with session.get(url1) as response:
                    data = await response.json()
                    keys = ["Name", "IP", "Port", "NumPlayers", "DayTime", "MapName", "DayTime"]
                    embed = discord.Embed(title=f'Ark Server Lookup results for: {name1}', description=f'Requested by: **{interaction.user.mention}**',color = green)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/818602996811169832/818942658176483338/58482958cef1014c0b5e49fa.png")
                    dedipop = {'xunmax':0,
                               'xunpop':0,
                               'psunmax':0,
                               'psunpop':0}
                    for item in data:
                        if name1.lower() in item["Name"].lower():
                            dedipop['psunpop'] += item['NumPlayers']
                            dedipop['psunmax'] += item['MaxPlayers'] 
                            embed.add_field(name=f'{item["Name"]}', value=f'''
**IP: **`{item["IP"]}`
**Port: **`{item["Port"]}`
**Players: **`{item["NumPlayers"]}/{item["MaxPlayers"]}`
**Map: **`{item["MapName"]}`
''', inline=False)
                embed.set_footer(text=f"↪ Total Population: {dedipop['psunpop']}/{dedipop['psunmax']}")
                await interaction.response.send_message(embed=embed)

@client.tree.command(name="serverpop")
async def xun(interaction: discord.Interaction):
     with sqlite3.connect("freewlbot.db") as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT clustername FROM clusterinfo WHERE guild_id = {interaction.guild.id}")
        namea = cursor.fetchone()
        name1 = namea[0]
        url1 = ("http://arkdedicated.com/ps4/cache/unofficialserverlist.json")
        async with ClientSession() as session:
                async with session.get(url1) as response:
                    data = await response.json()
                    keys = ["Name", "IP", "Port", "NumPlayers", "DayTime", "MapName", "DayTime"]
                    dedipop = {'xunmax':0,
                               'xunpop':0,
                               'psunmax':0,
                               'psunpop':0}
                    for item in data:
                        if name1.lower() in item["Name"].lower():
                            dedipop['psunpop'] += item['NumPlayers']
                            dedipop['psunmax'] += item['MaxPlayers'] 
                embed = discord.Embed(title=f"<:arrowarc:1128011993555677214> Total Server Population: {dedipop['psunpop']}/{dedipop['psunmax']}", description=f'Requested by: **{interaction.user.mention}**', color = green)    
                await interaction.response.send_message(embed=embed)                

@client.tree.command(name="help")
async def help (interaction: discord.Interaction):
     embed = discord.Embed(description = f"**ARC Guide** \n\n **``/setup`` Takes You Through The Setup Guide For The Bot** \n`/helpsetup` \n `/ban` \n `/configs` \n `/discord` \n `/freewl` \n `/help` \n `/helpsetup` \n `/nitradoping` \n `/playersearch` \n `/reportbug` \n `/resetseason` \n `/serverpop` \n `/tokenadd` \n `/whitelistrefresh` \n `/whitelistredeem` \n `/serverinfo` \n `/start` \n `/stopall` \n `/unban` \n\n\n Support Discord: [Click This](https://discord.gg/5VX8XBrcZB)", color = black)      
     embed.set_thumbnail(url = "https://cdn.dribbble.com/users/1007527/screenshots/2992564/arc-logo.png")
     iconURL = 'https://i.imgur.com/f4hkXHI.png'
     embed.set_author(name=f"ARC Help Guide" ,icon_url=iconURL)
     await interaction.response.send_message(embed=embed)

@client.tree.command(name="helpsetup")
async def helpsetup (interaction: discord.Interaction):
     embed = discord.Embed(description = f"https://discord.gg/5VX8XBrcZB", color = black)      
     embed.set_thumbnail(url = "https://cdn.dribbble.com/users/1007527/screenshots/2992564/arc-logo.png")
     await interaction.response.send_message(embed=embed)     

@client.tree.command(name="discord")
async def dc(interaction: discord.Interaction):
     embed = discord.Embed(description = f"https://discord.gg/5VX8XBrcZB", color = black)      
     embed.set_thumbnail(url = "https://cdn.dribbble.com/users/1007527/screenshots/2992564/arc-logo.png")
     await interaction.response.send_message(embed=embed)                       

@client.tree.command(name="nitradoping")
async def ping(interaction:discord.Interaction):
    async with ClientSession() as session:
        url = f"https://api.nitrado.net/ping"
        async with session.get(url) as response:
            p = await response.json()
            if str(p['status']) == str("success"):
                embed = discord.Embed(description=f"<:onlinearc:1131281660588064998> | `Nitrado API is Online` \n\n Status: 200 \n\n API working and healthy \n\n Any Issues? Checkout Nitrados Twitter \n <a:downarrow:1131282335027961966> \n https://twitter.com/Nitrado_EN", color = yellow)
                embed.set_thumbnail(url ="https://cdn.discordapp.com/attachments/1125577335375134771/1131282078193963109/nitradopfp.png")
                await interaction.response.send_message(embed=embed)
            else:
                embed = discord.Embed(description=f"`Nitrado API is Offline \n\n Status: 503 \n\n API is offline \n\n Any Issues? Checkout Nitrados Twitter -> https://twitter.com/Nitrado_EN`", color = red)
                await interaction.response.send_message(embed=embed)

@client.tree.command(name="freewl", description="Use This To Provide Free Whitelist For Players on One Map.")
@discord.app_commands.checks.cooldown(1, 360.0)
async def freewl(interaction: discord.Interaction, psn: str):
    try:
        with sqlite3.connect("freewlbot.db") as db:
            cursor = db.cursor()

            cursor.execute(f"SELECT question FROM freewlverify WHERE guild_id = {interaction.guild.id}")
            question_result = cursor.fetchone()

            if not question_result or question_result[0] in ["Yes", "None"]:
                cursor.execute(f"SELECT services, freewlmap, freewlchannel FROM clusterinfo WHERE guild_id = {interaction.guild.id}")
                services, freewlid1, wlchannel1 = cursor.fetchone()

                if interaction.channel.mention == wlchannel1:
                    embed1 = discord.Embed(description=f'Free Whitelisting {psn} Please Wait, This could take up to 30 seconds.')
                    await interaction.response.send_message(embed=embed1)
                    a = await aids(interaction)

                    url1 = f"https://api.nitrado.net/services/{freewlid1}/gameservers"
                    async with ClientSession() as session:
                        async with session.get(url1, headers=a) as response:
                            response_data = await response.json()
                            res = response_data.get("data", {}).get("gameserver", {}).get("query", {})
                            name = res.get("server_name", "")

                    url4 = f"https://api.nitrado.net/services/{freewlid1}/gameservers/games/whitelist?identifier={psn}"
                    async with ClientSession() as session:
                        async with session.post(url4, headers=a) as response:
                            p = await response.json()
                            status = str(p.get("status", ""))
                            
                            if str(p['status']) == "success":
                                await interaction.edit_original_response(embed=discord.Embed(description=f":crown: | {psn} Was Whitelisted on {name}",color = green))
                            elif str(p['status']) == "error":
                                if p['message'] == "Can't add the user to the whitelist.":
                                    await interaction.edit_original_response(embed=discord.Embed(description=f":crown: | {psn} Was Whitelisted on {name}",color = green))
                                elif p['message'] !=  "Can't add the user to the whitelist.":
                                    await interaction.edit_original_response(embed=discord.Embed(description=f":crown: | {p['message']}",color = red))
                else:
                    await interaction.channel.send("Wrong Channel, Please Try Again In The Correct Channel")
            else:
                await interaction.channel.send("Cannot perform free whitelist. Please check if your server allows it and make sure your PSN is linked to the bot.")

    except Exception as e:
        print(f"An error occurred: {e}")
        await interaction.channel.send(f"An error occurred while processing your request. Please try again later.")
        raise  


@client.tree.command(name="whitelist", description="Use This To Manually Whitelist On All Maps On Your Nitrado Account.")
async def whitelist(interaction: discord.Interaction, psn: str):
    with sqlite3.connect("freewlbot.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT services FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
        server_ids = cursor.fetchone()[0]
        cursor.close()

    url = "https://api.nitrado.net/services/{}/gameservers/games/whitelist?identifier={}"

    if isinstance(server_ids, int):
        server_ids = [str(server_ids)]
    else:
        server_ids = server_ids.split(",")

    tasks = []
    async with ClientSession() as session:
        for server_id in server_ids:
            header = await aids(interaction)
            task = asyncio.create_task(session.post(url.format(server_id, psn), headers=header))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        successful_count = 0
        unsuccessful_count = 0

        for response in responses:
            data = await response.json()
            if data["status"] == "success":
                successful_count += 1
            else:
                unsuccessful_count += 1

    successful_embed = discord.Embed(description=f"<:onlinearc:1131281660588064998> | {psn} was whitelisted on {successful_count} server(s).", color=green)
    unsuccessful_embed = discord.Embed(description=f":red_circle: | {psn} was not recognized on {unsuccessful_count} server(s).", color=red)

    await interaction.response.send_message(embed=successful_embed if successful_count > 0 else unsuccessful_embed)

def setup_database():
    conn = sqlite3.connect("freewlbot.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS whitelist_tokens (token_id INTEGER PRIMARY KEY AUTOINCREMENT, discord_id INTEGER, server_name TEXT, tokens INTEGER)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS whitelisted_players (discord_id INTEGER PRIMARY KEY AUTOINCREMENT, gamertag TEXT)"
    )
    conn.commit()
    cursor.close()
    conn.close()

@client.tree.command(name="tokenadd", description="Use This To Give A Player A Redeemable Token For Whitelist.")
async def tokenadd(interaction: discord.Interaction, user: discord.Member, token_count: int):
    author_id = interaction.user.id
    with sqlite3.connect("freewlbot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT guild_id FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
        guild_id = cursor.fetchone()[0]
        cursor.execute("SELECT clustername FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
        name = cursor.fetchone()[0]
        cursor.execute("SELECT guild_id, tokens FROM whitelist_tokens WHERE discord_id = ? AND guild_id = ?",
                       (user.id, guild_id))
        result = cursor.fetchone()

        if result:
            existing_tokens = result[1]
            tokens = existing_tokens + token_count
            cursor.execute("UPDATE whitelist_tokens SET tokens = ? WHERE discord_id = ? AND guild_id = ?",
                           (tokens, user.id, guild_id))
        else:
            cursor.execute("INSERT INTO whitelist_tokens (discord_id, guild_id, tokens) VALUES (?, ?, ?)",
                           (user.id, guild_id, token_count))
        
        conn.commit()


        cursor.execute("SELECT tokens FROM whitelist_tokens WHERE guild_id = ? AND discord_id = ?", (interaction.guild.id, user.id,))
        updatedtokens = cursor.fetchone()[0]
        emoji = "<:arc2:1129198621972250745>"
        embed = discord.Embed(description=f"{user.mention} Now Has `{updatedtokens}x` Token(s) Useable For Whitelist \n\n **Refreshes The Whitelist For ALL PSN's** \n ```/whitelistrefresh``` \u200b \n **Add's Whitelist On For More PSN's** ```/whitelistredeem```",color=green)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1125440198289928204/1130139451516006591/token-removebg-preview.png")
        iconURL = 'https://i.imgur.com/f4hkXHI.png'
        time = datetime.datetime.utcnow()
        embed.timestamp = (time)
        embed.set_author(name=f"| Added Token(s) To {user.display_name}'s Account",icon_url=iconURL)
        await interaction.response.send_message(embed=embed)

@client.tree.command(name="whitelistredeem",description="Players Can Use This To Redee Their Given Tokens For Whitelist.")
async def whitelistredeem(interaction: discord.Interaction, gamertag: str):
    author_id = interaction.user.id
    user = interaction.user
    with sqlite3.connect("freewlbot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT guild_id FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
        guild_id = cursor.fetchone()[0]
        cursor.execute("SELECT clustername FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
        name = cursor.fetchone()[0]
        cursor.execute("SELECT tokens FROM whitelist_tokens WHERE discord_id = ? AND guild_id = ? AND tokens > 0",
                       (user.id, guild_id))
        result = cursor.fetchone()
        url3 = "https://imgur.com/a/iySS09v"

        if result:
            tokens = result[0]
            url = "https://api.nitrado.net/services/{}/gameservers/games/whitelist?identifier={}"
            cursor.execute("SELECT services FROM clusterinfo WHERE guild_id = ?", (guild_id,))
            server_ids_result = cursor.fetchone()[0]
            server_ids = []

            if server_ids_result:
                if isinstance(server_ids_result, str):
                    server_ids = server_ids_result.split(",")
                else:
                    server_ids = [str(server_ids_result)]

            tasks = [] 

            async with ClientSession() as session:
                for server_id in server_ids:
                    header = await aids(interaction)
                    task = asyncio.create_task(session.post(url.format(server_id, gamertag), headers=header))
                    tasks.append(task)

                responses = await asyncio.gather(*tasks)

            success_responses = [response for response in responses if response.status == 200]

            if success_responses:
                tokens -= 1
                cursor.execute("UPDATE whitelist_tokens SET tokens = ? WHERE discord_id = ? AND guild_id = ?",
                               (tokens, user.id, guild_id))
                conn.commit()

                cursor.execute("INSERT INTO whitelisted_players (discord_id, gamertag, guild_id) VALUES (?, ?, ?)",
                               (user.id, gamertag, guild_id))
                conn.commit()
                cursor.close()
                await interaction.response.send_message(
                    f"Player **{gamertag}** has been whitelisted on Server **{name}** for user **{user.display_name}**."
                )
            else:
                await interaction.response.send_message("PSN is not valid.")
        else:
            await interaction.response.send_message(
                f"{user.display_name} does not have any whitelist tokens for Server **{name}**."
            )


@client.tree.command(name="whitelistrefresh",description="Use This To Refresh Your Whitelist If You Have Redeemed A Token.")
async def whitelistrefresh(interaction: discord.Interaction):
    await interaction.response.defer()
    author_id = interaction.user.id
    user = interaction.user
    with sqlite3.connect("freewlbot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT guild_id FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
        guild_id = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT gamertag) FROM whitelisted_players WHERE discord_id = ? AND guild_id = ?", (user.id, guild_id))
        refreshed_count = cursor.fetchone()[0]

        if refreshed_count > 0:
            server_ids = []
            with sqlite3.connect("freewlbot.db") as conn2:
                cursor2 = conn2.cursor()
                cursor2.execute("SELECT services FROM clusterinfo WHERE guild_id = ?", (guild_id,))
                server_ids = cursor2.fetchone()[0]
                cursor2.close()

            if isinstance(server_ids, str):
                server_ids = server_ids.split(",")
            else:
                server_ids = [str(server_ids)]

            cursor.execute("SELECT DISTINCT gamertag FROM whitelisted_players WHERE discord_id = ? AND guild_id = ?", (user.id, guild_id))
            gamertags = cursor.fetchall()
            cursor.execute("SELECT clustername FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
            name = cursor.fetchone()[0]

            url = "https://api.nitrado.net/services/{}/gameservers/games/whitelist?identifier={}"

            tasks = []
            async with ClientSession() as session:
                successful_count = 0
                for gamertag in gamertags:
                    for server_id in server_ids:
                        header = await aids(interaction)
                        task = asyncio.create_task(session.post(url.format(server_id, gamertag[0]), headers=header))
                        tasks.append(task)
                        successful_count += 1

                await asyncio.gather(*tasks)

            message = f"Refreshed whitelist for {refreshed_count} gamertag(s) on Server **{name}**."
        else:
            message = f"No whitelisted players found for user **{user.display_name}** on Server **{name}**."

        await interaction.followup.send(content=message)


@client.tree.command(name="ban", description="Use This To Ban A Player On Your Given Servers")
async def ban(interaction: discord.Interaction, psn: str, reason: str):
    with sqlite3.connect("freewlbot.db") as db:
        psn = psn.lower()
        cursor = db.cursor()
        cursor.execute("SELECT services FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
        server_ids = cursor.fetchone()[0]

    url = "https://api.nitrado.net/services/{}/gameservers/games/banlist?identifier={}"
    cursor.execute("SELECT clustername FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
    clustername = cursor.fetchone()[0]
    if isinstance(server_ids, int):
        server_ids = [str(server_ids)]
    else:
        server_ids = server_ids.split(",")

    tasks = []
    async with ClientSession() as session:
        for server_id in server_ids:
            header = await aids(interaction)
            task = asyncio.create_task(session.post(url.format(server_id, psn), headers=header))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        successful_count = 0
        unsuccessful_count = 0

        for response in responses:
            data = await response.json()
            if data["status"] == "success":
                successful_count += 1
            else:
                unsuccessful_count += 1

    successful_embed = discord.Embed(description=f"{psn} was Banned on {successful_count} server(s).")
    unsuccessful_embed = discord.Embed(description=f"{psn} was not recognized on {unsuccessful_count} server(s).")

    cursor.execute("SELECT psn FROM bannedplayers WHERE server = ? AND psn = ?", (clustername, psn))
    existing_entry = cursor.fetchone()
    
    if existing_entry:
        cursor.execute("UPDATE bannedplayers SET reason = ?, time = ?  WHERE server = ? AND psn = ?", (reason,datetime.datetime.now(), clustername, psn))
    else:
        cursor.execute("INSERT INTO bannedplayers (psn,time, reason, server) VALUES (?, ?, ?, ?)", (psn, datetime.datetime.now(), reason, clustername))
    
    db.commit()
    cursor.close()

    await interaction.response.send_message(embed=successful_embed if successful_count > 0 else unsuccessful_embed)

@client.tree.command(name="searchpsn", description="Use This To Search PSNs on Discord For Information")
async def searchpsns(interaction: discord.Interaction, psn: str):
    with sqlite3.connect("freewlbot.db") as db:
        psn = psn.lower()
        cursor = db.cursor()
        cursor.execute("SELECT psn, reason, server, time FROM bannedplayers WHERE psn = ?", (psn,))
        psnlist = cursor.fetchall()

        ban_info = []

        for result in psnlist:
            psn, reason, server, time = result
            ban_info.append(f"Server: **{server}** \nReason: {reason} \nDate: {time} ")

        ban_info_str = "\n\n".join(ban_info)

        cursor.execute(f"SELECT dcname FROM linkedpsn WHERE psn = ?", (psn.lower(),))
        data1 = cursor.fetchone() 
        linkedpsn = data1[0] if data1 else "No Linked Account Currently"  

        embed = discord.Embed(
            title=f"ARC Search For -> {psn}",
            description=f"`Ban List`\n\n {ban_info_str}\n\nLinked Account Is: {linkedpsn}",
            color=0xFF0000
        )

        if interaction.guild and interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url) 
            iconURL = 'https://i.imgur.com/f4hkXHI.png'
            embed.set_author(name=f"| ARC PSN Search",icon_url=iconURL)
        await interaction.response.send_message(embed=embed)



@client.tree.command(name="stopall", description="Use This To Stop ALL Servers On Your Account.")
async def stop_all_servers(interaction: discord.Interaction):
    with sqlite3.connect("freewlbot.db") as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT services FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
        server_ids = cursor.fetchone() 
        if server_ids:
            server_ids = server_ids[0]
            serveridlist = [server_ids] 

            embed1 = discord.Embed(description="<a:loading:900792389449445447> | Stopping all servers. Please wait, this could take some time.")
            await interaction.response.send_message(embed=embed1)
            a = await aids(interaction)

            for i in serveridlist:
                url = f"https://api.nitrado.net/services/{i}/gameservers/games/stop"
                async with ClientSession() as session:
                    async with session.post(url, headers=a) as response:
                        print(response)
                        p = await response.json()
                        print(p)

            if str(p['status']) == str("success"):
                successful = discord.Embed(description=f"<:doom_black_crown:1076648431440891974> | All servers have been stopped.")
                await interaction.edit_original_response(embed=successful)
            elif str(p['status']) == str("error"):
                unsuccessful = discord.Embed(description="<:blackalr:944129017517334638> | Failed to stop servers. Please try again.")
                await interaction.edit_original_response(embed=unsuccessful)
        else:
            await interaction.channel.send("No servers found in the database.")



@client.tree.command(name="start", description="Use This To Start All Servers On Your Nitrado Account")
async def start_all_servers(interaction: discord.Interaction):
    with sqlite3.connect("freewlbot.db") as db:
        serveridlist = []
        cursor = db.cursor()
        cursor.execute(f"SELECT services FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
        serverids = cursor.fetchall()
        for x in serverids:
            x = x[0]
            serveridlist.extend(x.split(","))  
            if isinstance(server_ids, int):
                server_ids = [str(server_ids)]
            else:
                server_ids = server_ids.split(",")
        
        embed1 = discord.Embed(description="<a:loading:900792389449445447> | Starting all servers. Please wait, this could take some time.")
        await interaction.response.send_message(embed=embed1)
        a = await aids(interaction)
        
        for i in serveridlist:
            url = f"https://api.nitrado.net/services/{i}/gameservers/games/start"
            async with ClientSession() as session:
                async with session.post(url, headers=a) as response:
                    print(response)
                    p = await response.json()
                    print(p)
        
        if str(p['status']) == str("success"):
            successful = discord.Embed(description=f"<:doom_black_crown:1076648431440891974> | All servers have been started.")
            await interaction.edit_original_response(embed=successful)
        elif str(p['status']) == str("error"): 
            unsuccessful = discord.Embed(description="<:blackalr:944129017517334638> | Failed to start servers. Please try again.")
            await interaction.edit_original_response(embed=unsuccessful)


@client.tree.command(name="unban", description="Use This To Unban A Player on All Your Servers.")
async def unban(interaction: discord.Interaction, psn: str):
    with sqlite3.connect("freewlbot.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT services FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
        server_ids = cursor.fetchone()[0]
        cursor.close()

    if isinstance(server_ids, int):
        server_ids = [str(server_ids)]
    else:
        server_ids = server_ids.split(",")

    url = "https://api.nitrado.net/services/{}/gameservers/games/banlist?identifier={}"

    tasks = []
    async with ClientSession() as session:
        for server_id in server_ids:
            header = await aids(interaction)
            task = asyncio.create_task(session.delete(url.format(server_id, psn), headers=header))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        successful_count = 0
        unsuccessful_count = 0

        for response in responses:
            data = await response.json()
            if data["status"] == "success":
                successful_count += 1
            else:
                unsuccessful_count += 1

    successful_embed = discord.Embed(description=f"{psn} was Unbanned on {successful_count} server(s).")
    unsuccessful_embed = discord.Embed(description=f"{psn} was not recognized on {unsuccessful_count} server(s).")

    await interaction.response.send_message(embed=successful_embed if successful_count > 0 else unsuccessful_embed)           

@client.event
async def on_ready():
    activity = discord.Game(name="ARC Admin Helper | Made For Nitrado", type=3)
    await client.change_presence(status=discord.Status.idle, activity=activity)
    print("Bot is ready!")
    try:
        synced = await client.tree.sync()
        print(f"Synched {len(synced)} command(s)")
        loop.create_task(status_task())
        logdaloop.start()
        admin_log_loop.start()
        update_member_count.start()
        client.add_view(SelectView(client))
    except Exception as e:
        print(e)


class Select(discord.ui.Select):
    def __init__(self, original_embed):
        options = [
            discord.SelectOption(label="Bot Info", value="bot_info"),
            discord.SelectOption(label="Change Outputs", value="change_output"),
        ]
        super().__init__(placeholder="Select an option", options=options)
        self.original_embed = original_embed

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "bot_info":
            with sqlite3.connect("freewlbot.db") as db:
                cursor = db.cursor()
                cursor.execute("SELECT services FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
                result = cursor.fetchone()
                if result is None:
                    services = "No services found"
                else:
                    services = result[0]
            embed = discord.Embed(description=f"**ARC Bot Info**\n ➤ Server Name: {interaction.guild.name} \n➤ Support Discord: [Click This](https://discord.gg/5VX8XBrcZB) \n➤ Service ID's: `{services}`\n ➤ Discords Operating In: `{len(client.guilds)}`\n ➤ Owner: <@680574573665583144>")
            iconURL = 'https://i.imgur.com/f4hkXHI.png'
            embed.set_author(name=f"| ARC Bot Information",icon_url=iconURL)
            view1 = BotSelectView(original_embed=self.original_embed)
            await interaction.response.edit_message(embed=embed, view=view1)
        if self.values[0] == "change_output":
            embed1 = discord.Embed(description="**Options:** \n **__Select These Options From The Menu Below__** \n ➤ Change Server Name \n ➤ Automatically Update Server ID's \n ➤ Change FreeWLMap Server ID \n ➤ Update Channel For Free WL commands \n ➤ Update Status Channel \n ➤ Update Admin Logging Channel")
            iconURL = 'https://i.imgur.com/f4hkXHI.png'
            embed1.set_author(name=f"| ARC Bot Configs",icon_url=iconURL)
            view2 = ChangeNameView(original_embed=self.original_embed)
            await interaction.response.edit_message(embed=embed1, view=view2)
            return

        view = SelectView(original_embed=self.original_embed)
        await interaction.response.edit_message(embed=self.original_embed, view=view)

class BackButton(discord.ui.Button):
    def __init__(self, original_embed):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary)
        self.original_embed = original_embed

    async def callback(self, interaction: discord.Interaction):
        embed = self.original_embed.copy()
        view = SelectView(original_embed=self.original_embed)
        await interaction.response.edit_message(embed=embed, view=view)


class SelectView(discord.ui.View):
    def __init__(self, original_embed=None, *, timeout=180):
        super().__init__(timeout=timeout)
        self.original_embed = original_embed
        self.select = Select(original_embed)
        self.add_item(self.select)
        self.add_item(BackButton(original_embed))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == interaction.message.interaction.user

    async def on_timeout(self):
        if self.original_embed is not None and self.message is not None:
            try:
                await self.message.edit(embed=discord.Embed(description="Selection timed out."))
            except discord.errors.NotFound:
                pass

class BotSelectView(discord.ui.View):
    def __init__(self, original_embed=None, *, timeout=180):
        super().__init__(timeout=timeout)
        self.original_embed = original_embed
        self.bot_select = BotSelect(original_embed)
        self.add_item(self.bot_select)
        self.add_item(BackButton(original_embed))
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == interaction.message.interaction.user


class BotSelect(discord.ui.Select):
    def __init__(self, original_embed):
        options = [
            discord.SelectOption(label="Send Server ID's for Copy & Paste", value="serverids"),
        ]
        super().__init__(placeholder="Select an option", options=options)
        self.original_embed = original_embed

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "serverids":
                with sqlite3.connect("freewlbot.db") as db:
                    cursor = db.cursor()
                    cursor.execute("SELECT services FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
                    services = cursor.fetchone()[0]
                    await interaction.response.send_message(f"{services}")
                    return

class ChangeNameView(discord.ui.View):
    def __init__(self, original_embed=None, *, timeout=180):
        super().__init__(timeout=timeout)
        self.original_embed = original_embed
        self.bot_select = ChangeName(original_embed)
        self.add_item(self.bot_select)
        self.add_item(BackButton(original_embed))
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == interaction.message.interaction.user


class ChangeName(discord.ui.Select):
    def __init__(self, original_embed):
        options = [
            discord.SelectOption(label="Change Cluster Name", value="changeclustername"),
            discord.SelectOption(label="Update Server ID's", value="updateserverids"),
            discord.SelectOption(label="Change FreeWLMap ID", value="changewlserverid"),
            discord.SelectOption(label="Change FreeWLMap Channel", value="changefreewlchannel"),
            discord.SelectOption(label="Change Status Channel", value="changestatuschannel"),
            discord.SelectOption(label="Change Tribe Warn Channel", value="changetribewarnchannel"),
            discord.SelectOption(label="Change Admin Logging Channel", value="adminloggingchannel"),

        ]
        super().__init__(placeholder="Select an option", options=options)
        self.original_embed = original_embed
        self.client = client
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if self.values[0] == "changeclustername":
            embed = discord.Embed(description="Please **REPLY USING DISCORD'S REPLY FEATURE TO THIS MESSAGE** with your new cluster name")
            embed.set_footer(text="Closes in 60 Seconds | ARC Helper")
            msg1 = await interaction.followup.send(embed=embed)
            message_id = msg1.id

            def check(m):
                return (
                    m.author == interaction.user
                    and m.reference
                    and m.reference.message_id == message_id
                )

            try:
                msg = await self.client.wait_for('message', timeout=60.0, check=check)
                if msg.reference and msg.reference.message_id == message_id:
                    new_cluster_name = msg.content
                    print(new_cluster_name)
                    embed1 = discord.Embed(description=f"Thanks, Your New Cluster Name Has Been Updated and Is Now {new_cluster_name}", color=discord.Color.green())
                    await interaction.followup.edit_message(embed=embed1, message_id=message_id)
                    with sqlite3.connect("freewlbot.db") as db:
                        cursor = db.cursor()
                        cursor.execute("SELECT clustername FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
                        data = cursor.fetchall()
                        print(data)
                        if data:
                            cursor.execute(
                                "UPDATE clusterinfo SET clustername = ? WHERE guild_id = ?",
                                (new_cluster_name, interaction.guild.id)
                            )
                            db.commit()
                            cursor.close()
                        else:
                            cursor.execute(
                                "INSERT INTO clusterinfo (guild_id, clustername) VALUES (?, ?)",
                                (interaction.guild.id, new_cluster_name)
                            )
                            db.commit()
                            cursor.close()
            except asyncio.TimeoutError:
                return
        
        if self.values[0] == "changewlserverid":
            embed = discord.Embed(description="Please **REPLY USING DISCORD'S REPLY FEATURE TO THIS MESSAGE** with your new WL Server ID")
            embed.set_footer(text="Closes in 60 Seconds | ARC Helper")
            msg1 = await interaction.followup.send(embed=embed)
            message_id = msg1.id

            def check(m):
                return (
                    m.author == interaction.user
                    and m.reference
                    and m.reference.message_id == message_id
                )

            try:
                print("aaaa")
                msg = await self.client.wait_for('message', timeout=60.0, check=check)
                if msg.reference and msg.reference.message_id == message_id:
                    freewlserverid = msg.content
                    embed1 = discord.Embed(description=f"Thanks, Your New Free WL Server ID Has Been Updated and Is Now {freewlserverid}", color=discord.Color.green())
                    await interaction.followup.edit_message(embed=embed1, message_id=message_id)
                    with sqlite3.connect("freewlbot.db") as db:
                        cursor = db.cursor()
                        cursor.execute("SELECT freewlmap FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
                        data = cursor.fetchall()
                        print(data)
                        if data:
                            cursor.execute(
                                "UPDATE clusterinfo SET freewlmap = ? WHERE guild_id = ?",
                                (freewlserverid, interaction.guild.id)
                            )
                            db.commit()
                            cursor.close()
                        else:
                            cursor.execute(
                                "INSERT INTO clusterinfo (guild_id, freewlmap) VALUES (?, ?)",
                                (interaction.guild.id, freewlserverid)
                            )
                            db.commit()
                            cursor.close()
            except asyncio.TimeoutError:
                return

        if self.values[0] == "updateserverids":
            print("aids")
            with sqlite3.connect("freewlbot.db") as db:
                cursor = db.cursor()
                cursor.execute("SELECT services FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
                data = cursor.fetchall()[0]
                url1 = "https://api.nitrado.net/services"
                a = await aids(interaction)
                async with ClientSession() as session:
                    async with session.get(url1, headers=a) as response:
                        response = await response.json()
                        res = response["data"]["services"]
                        service_list = []
                        for services in res:
                            service_list.append(services["id"])
                        contexts = str(service_list)
                        string_without_brackets = re.sub(r"[\[\]]", '', contexts)
                        cursor.execute(
                            "UPDATE clusterinfo SET services = ? WHERE guild_id = ?",
                            (string_without_brackets, interaction.guild.id)
                        )
                        if cursor.rowcount == 0:
                            cursor.execute(
                                "INSERT INTO clusterinfo (services, guild_id) VALUES (?, ?)",
                                (string_without_brackets, interaction.guild.id)
                            )
                        db.commit()
            cursor.close()

            embed3 = discord.Embed(description="Successfully Updated Server ID List From Nitrado")
            await interaction.followup.send(embed=embed3)

        if self.values[0] == "changefreewlchannel":
            embed = discord.Embed(description="Please **REPLY USING DISCORD'S REPLY FEATURE TO THIS MESSAGE** `mentioning` the new Free WL channel")
            embed.set_footer(text="Closes in 60 Seconds | ARC Helper")
            msg1 = await interaction.followup.send(embed=embed)
            message_id = msg1.id

            def check(m):
                return (
                    m.author == interaction.user
                    and m.reference
                    and m.reference.message_id == message_id
                )

            try:
                msg = await self.client.wait_for('message', timeout=60.0, check=check)
                if msg.reference and msg.reference.message_id == message_id:
                    freewlchannel = msg.content
                    embed1 = discord.Embed(description=f"Thanks, Your New Free WL Channel Has Been Updated and Is Now {freewlchannel}", color=discord.Color.green())
                    await interaction.followup.edit_message(embed=embed1, message_id=message_id)
                    with sqlite3.connect("freewlbot.db") as db:
                        cursor = db.cursor()
                        cursor.execute("SELECT freewlchannel FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
                        data = cursor.fetchall()
                        print(data)
                        if data:
                            cursor.execute(
                                "UPDATE clusterinfo SET freewlchannel = ? WHERE guild_id = ?",
                                (freewlchannel, interaction.guild.id)
                            )
                            db.commit()
                            cursor.close()
                        else:
                            cursor.execute(
                                "INSERT INTO clusterinfo (guild_id, freewlchannel) VALUES (?, ?)",
                                (interaction.guild.id, freewlchannel)
                            )
                            db.commit()
                            cursor.close()
            except asyncio.TimeoutError:
                return
        if self.values[0] == "changestatuschannel":
            embed = discord.Embed(description="Please **REPLY USING DISCORD'S REPLY FEATURE TO THIS MESSAGE** `mentioning` the new Status Embed Channel")
            embed.set_footer(text="Closes in 60 Seconds | ARC Helper")
            msg1 = await interaction.followup.send(embed=embed)
            message_id = msg1.id

            def check(m):
                return (
                    m.author == interaction.user
                    and m.reference
                    and m.reference.message_id == message_id
                )

            try:
                msg = await self.client.wait_for('message', timeout=60.0, check=check)
                if msg.reference and msg.reference.message_id == message_id:
                    statusembedchannel = msg.content
                    embed1 = discord.Embed(description=f"Thanks, Your New Status Embed Channel Has Been Updated and Is Now {statusembedchannel}", color=discord.Color.green())
                    await interaction.followup.edit_message(embed=embed1, message_id=message_id)
                    with sqlite3.connect("freewlbot.db") as db:
                        cursor = db.cursor()
                        cursor.execute("SELECT freewlchannel FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
                        data = cursor.fetchall()
                        print(data)
                        if data:
                            cursor.execute(
                                "UPDATE clusterinfo SET statuschannel = ? WHERE guild_id = ?",
                                (statusembedchannel, interaction.guild.id)
                            )
                            db.commit()
                            cursor.close()
                        else:
                            cursor.execute(
                                "INSERT INTO clusterinfo (guild_id, statuschannel) VALUES (?, ?)",
                                (interaction.guild.id, statusembedchannel)
                            )
                            db.commit()
                            cursor.close()
            except asyncio.TimeoutError:
                return

        if self.values[0] == "changetribewarnchannel":
            embed = discord.Embed(description="Please **REPLY USING DISCORD'S REPLY FEATURE TO THIS MESSAGE** `mentioning` the new Tribe Warnings Channel")
            embed.set_footer(text="Closes in 60 Seconds | ARC Helper")
            msg1 = await interaction.followup.send(embed=embed)
            message_id = msg1.id

            def check(m):
                return (
                    m.author == interaction.user
                    and m.reference
                    and m.reference.message_id == message_id
                )

            try:
                msg = await self.client.wait_for('message', timeout=60.0, check=check)
                if msg.reference and msg.reference.message_id == message_id:
                    tribewarnchannel = msg.content
                    embed1 = discord.Embed(description=f"Thanks, Your New Tribe Warn Channel Has Been Updated and Is Now {tribewarnchannel}", color=discord.Color.green())
                    await interaction.followup.edit_message(embed=embed1, message_id=message_id)
                    with sqlite3.connect("freewlbot.db") as db:
                        cursor = db.cursor()
                        cursor.execute("SELECT tribewarnchannel FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
                        data = cursor.fetchall()
                        print(data)
                        if data:
                            cursor.execute(
                                "UPDATE clusterinfo SET tribewarnchannel = ? WHERE guild_id = ?",
                                (tribewarnchannel, interaction.guild.id)
                            )
                            db.commit()
                            cursor.close()
                        else:
                            cursor.execute(
                                "INSERT INTO clusterinfo (guild_id, tribewarnchannel) VALUES (?, ?)",
                                (interaction.guild.id, tribewarnchannel)
                            )
                            db.commit()
                            cursor.close()
            except asyncio.TimeoutError:
                return
        if self.values[0] == "adminloggingchannel":
            embed = discord.Embed(description="Please **REPLY USING DISCORD'S REPLY FEATURE TO THIS MESSAGE** `mentioning` the new Admin Logging Channel")
            embed.set_footer(text="Closes in 60 Seconds | ARC Helper")
            msg1 = await interaction.followup.send(embed=embed)
            message_id = msg1.id

            def check(m):
                return (
                    m.author == interaction.user
                    and m.reference
                    and m.reference.message_id == message_id
                )

            try:
                msg = await self.client.wait_for('message', timeout=60.0, check=check)
                if msg.reference and msg.reference.message_id == message_id:
                    adminloggingchannel = msg.content
                    embed1 = discord.Embed(description=f"Thanks, Your New Admin Loggging Channel Has Been Updated and Is Now {adminloggingchannel}", color=discord.Color.green())
                    await interaction.followup.edit_message(embed=embed1, message_id=message_id)
                    with sqlite3.connect(db_file) as db:
                        cursor = db.cursor()
                        cursor.execute("SELECT admin_logging_channel FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
                        data = cursor.fetchall()
                        print(data)
                        if data:
                            cursor.execute(
                                "UPDATE clusterinfo SET admin_logging_channel = ? WHERE guild_id = ?",
                                (adminloggingchannel, interaction.guild.id)
                            )
                            db.commit()
                            cursor.close()
                        else:
                            cursor.execute(
                                "INSERT INTO clusterinfo (guild_id, admin_logging_channel) VALUES (?, ?)",
                                (interaction.guild.id, adminloggingchannel)
                            )
                            db.commit()
                            cursor.close()
            except asyncio.TimeoutError:
                return
@client.tree.command(name="configs", description="Use This To Configure Your ARC Experience")
async def menu(interaction: discord.Interaction):
    embed = discord.Embed(description="𝐀𝐑𝐂 𝐎𝐩𝐭𝐢𝐨𝐧𝐬: \n\n `Information` \n ➜ Get Current Server ID's, Bot Info And More! \n `Outputs` \n ➜ Customise **Your** ARC Experience Within Your Server.", color=green)
    embed.set_footer(text="𝘔𝘦𝘯𝘶 𝘊𝘭𝘰𝘴𝘦𝘴 𝘞𝘪𝘵𝘩𝘪𝘯 1 𝘮𝘪𝘯𝘶𝘵𝘦 𝘰𝘧 𝘪𝘯𝘢𝘤𝘵𝘪𝘷𝘪𝘵𝘺")
    iconURL = 'https://i.imgur.com/f4hkXHI.png'
    embed.set_author(name=f"| ARC CONFIG MENU", icon_url=iconURL)
    view = SelectView(original_embed=embed)
    message = await interaction.response.send_message(embed=embed, view=view)
    view.message = message

async def get_suspend_date(server_id, nitrado_token):
    url = f"https://api.nitrado.net/services/{server_id}/"
    headers = {
        "Authorization": f"Bearer {nitrado_token}"
    }

    async with ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    if "data" in data and "service" in data["data"] and "suspend_date" in data["data"]["service"]:
                        suspend_date = data["data"]["service"]["suspend_date"]
                        return suspend_date

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error in getting suspend_date for server {server_id}: {e}")

    return None 

async def check_status_registration(guild_id):
    with sqlite3.connect(db_file) as db:
        cursor = db.cursor()
        cursor.execute("SELECT token FROM tokens WHERE guild_id = ?", (guild_id,))
        redeemed_token = cursor.fetchone()

        if redeemed_token:
            return True
        else:
            return False

loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)

async def status_task():
    while True:
        try:
            with sqlite3.connect("freewlbot.db") as db:
                cursor = db.cursor()
                cursor.execute("SELECT guild_id, ntoken, services, statuschannel FROM clusterinfo")
                guild_infos = cursor.fetchall()
        except Exception as e:
            logging.error(f"Error fetching guild information from the database: {e}")
            traceback.print_exc()
            await asyncio.sleep(300)
            continue

        for guild_info in guild_infos:
            try:
                guild_id, nitrado_token, server_ids, status_channel_mention = guild_info
                print(guild_id)

                guild = client.get_guild(guild_id)
                if guild is None:
                    logging.warning(f"Guild with ID {guild_id} not found.")
                    continue
                
                status_channel_mention = str(status_channel_mention)
                channel_id_match = re.match(r"<#(\d+)>", status_channel_mention)
                print(status_channel_mention)
                if channel_id_match is None:
                    logging.warning(f"Invalid status channel mention for guild {guild.name}. Mention: {status_channel_mention}")
                    continue

                status_channel_id = int(channel_id_match.group(1))

                channel = guild.get_channel(status_channel_id)
                if channel is None:
                    logging.warning(f"Status channel with ID {status_channel_id} not found in guild {guild.name}.")

                    service_statuses = []
                    if server_ids:
                        server_ids_list = []
                        if isinstance(server_ids, int):
                            server_ids_list = [str(server_ids)]
                        else:
                            server_ids_list = server_ids.split(",")
                            for service_id in server_ids_list:
                                detailed_info_url = f"https://api.nitrado.net/services/{service_id}/gameservers"
                                suspend_date = await get_suspend_date(service_id, nitrado_token)
                                headers = {
                                    "Authorization": f"Bearer {nitrado_token}"
                                }
                                async with ClientSession() as session:
                                    try:
                                        async with session.get(detailed_info_url, headers=headers) as detailed_response:
                                            if detailed_response.status == 200:
                                                detailed_data = await detailed_response.json()
                                                if "data" in detailed_data and "gameserver" in detailed_data["data"]:
                                                    detailed_info = detailed_data["data"]["gameserver"]
                                                    if "query" in detailed_info:
                                                        player_current = detailed_info["query"].get("player_current", "N/A")
                                                    else:
                                                        player_current = "N/A"
                                                    server_name = detailed_info.get("query", {}).get("server_name", f"Server {service_id} Offline")
                                                    service_status = {
                                                        "name": server_name,
                                                        "slots": detailed_info.get("slots", "N/A"),
                                                        "players": player_current,
                                                        "max_players": detailed_info.get("query", {}).get("player_max", "N/A"),
                                                        "status": detailed_info.get("status", "N/A"),
                                                        "suspend_date": suspend_date
                                                    }
                                                    service_statuses.append(service_status)
                                    except Exception as e: 
                                        import traceback
                                        traceback.print_exc()
                                        print(f"Error in background task: {e}")
                    
                    update_date_unix = int(datetime.datetime.utcnow().timestamp())
                    embed = discord.Embed(title="**ARC Server Status**", timestamp=datetime.datetime.utcnow())
                    if service_statuses:
                        for service_status in service_statuses:
                            suspend_date_unix = datetime.datetime.fromisoformat(service_status['suspend_date']).replace(tzinfo=timezone.utc).timestamp()
                            status = "🟢" if service_status["status"] == "started" else "🔴" if service_status["status"] == "stopped" else "🟠" if service_status["status"] == "restarting" else "❓"
                            embed.add_field(
                                name=service_status["name"],
                                value=f"{status} Slots: {service_status['slots']}\nPlayers: {service_status['players']}/{service_status['max_players']}\nSuspend Date: <t:{int(suspend_date_unix)}:R>",
                                inline=False
                            )
                            print(service_statuses)
                    else:
                        embed.description = "No server information available."

                    last_message = None
                    async for message in channel.history(limit=1):
                        last_message = message
                    
                    print(embed)
                    if last_message is not None:
                        try:
                            print(f"Updating status in '{guild.name}' in channel '{channel.name}'.")
                            await last_message.edit(embed=embed)
                            print(f"Successfully updated status in '{guild.name}' in channel '{channel.name}'.")
                        except discord.errors.Forbidden as edit_error:
                            logging.warning(f"Error editing message in guild {guild.name}: {edit_error}")
                        
                    else:
                        print(f"Sending new status embed in '{guild.name}' in channel '{channel.name}'.")
                        await channel.send(embed=embed)
                        print(f"Successfully sent status embed in '{guild.name}' in channel '{channel.name}'.")

                await asyncio.sleep(120)
            
            except Exception as e:
                pass


@client.tree.command(name="playersearch", description="Use This To Search For Player Info On Your Servers")
async def search_gamertag(interaction: discord.Interaction, player_name: str):
    await interaction.response.defer()
    player_name = player_name.lower()
    
    if player_name == "human" or player_name == "mensch":
        await interaction.followup.send(f"Sorry, you cannot search for `{player_name}`")
    else:
        found_gamertag = False
        gamertags = []

        with sqlite3.connect("freewlbot.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT services FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
            server_ids = cursor.fetchone()[0]
            if isinstance(server_ids, int):
                server_ids = [str(server_ids)]
            else:
                server_ids = server_ids.split(",")
            cursor.execute("SELECT clustername FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
            name = cursor.fetchone()[0]

        with sqlite3.connect("freewlbot.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT gamertag FROM player_info WHERE clustername = ? AND playername = ?", (name, player_name))
            existing_gamertag = cursor.fetchone()
            if existing_gamertag:
                found_gamertag = True
                gamertags.append(existing_gamertag[0])

        log_directory = f"/root/{interaction.guild.id}/"
        log_files = [file for file in os.listdir(log_directory) if file.endswith(".log")]

        async def search_gamertag_in_file(file_path, player_name):
            gamertags = []
            async with aiofiles.open(file_path, mode="r") as file:
                log_lines = await file.readlines()

                for log_line in log_lines:
                    match = re.search(rf"\[\d{{4}}\.\d{{2}}\.\d{{2}}-\d{{2}}\.\d{{2}}.\d{{2}}:\d{{3}}]\[\d+].*?(\S+)\s*\({re.escape(player_name)}\):", log_line,re.IGNORECASE)
                    if match:
                        gamertag = match.group(1)
                        gamertags.append(gamertag)

            return gamertags

        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for log_file in log_files:
                file_path = os.path.join(log_directory, log_file)
                results.append(executor.submit(search_gamertag_in_file, file_path, player_name))

            for future in concurrent.futures.as_completed(results):
                log_gamertags = await future.result()
                if log_gamertags:
                    found_gamertag = True
                    gamertags.extend(log_gamertags)
                    with sqlite3.connect("freewlbot.db") as db:
                        cursor = db.cursor()
                        cursor.execute("INSERT INTO player_info (clustername, playername, gamertag) VALUES (?, ?, ?)",
                                       (name, player_name, log_gamertags[0]))

        response = f"No gamertag found for the player: '{player_name}'"
        if found_gamertag:
            embed = discord.Embed(description=f"<:arrowarc:1128011993555677214> Gamertag(s) for player name - `{player_name}`:", color=green)
            for gamertag in set(gamertags):
                embed.add_field(name="Potential Gamertag", value=gamertag, inline=False)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(content=response)



@client.tree.command(name="tribewarn", description="Use This To Warn A Tribe In Your Specified Channel.")
async def warn(interaction: discord.Interaction, reason:str, tribe:str, map:str, totalwarnings:str, ban: str = "N/A"):
        with sqlite3.connect("freewlbot.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT tribewarnchannel FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
            tribewarnchannel = cursor.fetchone()[0]
            print(tribewarnchannel)
            channel_id_match = re.match(r"<#(\d+)>", tribewarnchannel)
            new_channel_id = int(channel_id_match.group(1))
            print (new_channel_id)
            if new_channel_id is None:
                print(f"Invalid status channel mention for guild {interaction.guild.id}.")
            else:    
                cursor.execute("SELECT clustername FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
                name = cursor.fetchone()[0]
                embed = discord.Embed(description=f"**{name} Cluster Tribe Warning** \n\n - This Tribe Has Recieved A Warning For Breaking A Rule (Explained Below) \n\n **Map Involved** \n <:downarrow:1131681104127078511> `{map}` \n **Tribe** \n <:downarrow:1131681104127078511> `{tribe}` \n **Reason** \n <:downarrow:1131681104127078511> `{reason}` \n **Total Warnings** \n <:downarrow:1131681104127078511> `{totalwarnings}` \n **Admin Involved:** \n <:downarrow:1131681104127078511> {interaction.user.mention} \n **Tribe Ban** \n <:downarrow:1131681104127078511> {ban}", color = black)   
                channel = client.get_channel(new_channel_id)
                await channel.send(embed=embed)
                await interaction.response.send_message("Request Completed")

@client.tree.command(name="resetseason", description="Use This Before Wipe To Change Season.")
async def clearseason (interaction:discord.Interaction):
    with sqlite3.connect("freewlbot.db") as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM whitelist_tokens WHERE guild_id = ?", (interaction.guild.id,))
        deleted_tokens = cursor.rowcount
        cursor.execute("DELETE FROM whitelisted_players WHERE guild_id = ?", (interaction.guild.id,))
        deleted_players = cursor.rowcount
        db.commit()
        cursor.close()
        message = f"Reset successful! Deleted {deleted_tokens} tokens and {deleted_players} players."
        await interaction.response.send_message(message)


@client.tree.command(name="reportbug", description="Use This To Report Any Bugs In The Bot Directly To The Owner.")
async def reportbug (interaction: discord.Interaction, reason:str): 
     await interaction.response.send_message("Bug Successfully Reported, Thanks!")
     with sqlite3.connect("freewlbot.db") as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT clustername FROM clusterinfo WHERE guild_id = {interaction.guild.id}")
        reportname = cursor.fetchone()
        newname = reportname[0]
        takenGuild = client.get_guild(1125440197149065388)
        a = takenGuild.get_channel(1125442004394975293)
        embed = discord.Embed(description=f"**ARC 1.0 Bug Report** \n\n `Cluster Name:` {newname} \n\n `Bug:` \n {reason} <@680574573665583144>", color = red)
        await a.send(embed=embed)
        await a.send(f"<@680574573665583144>")

def get_random_string(length):
    result_str = ''.join(random.choice(string.ascii_uppercase) for i in range(length))
    return result_str

@client.tree.command(name="linkpsn", description="Use This To Link Your Playstation Account To Your Discord.")
async def linkpsn(interaction: discord.Interaction, psn: str):
    try:
        with sqlite3.connect("freewlbot.db") as db:
            cursor = db.cursor()

            psn = psn.lower()  

            cursor.execute("SELECT psn FROM linkedpsn WHERE psn = ?", (psn,))
            existing_psn = cursor.fetchone()

            if existing_psn:
                await interaction.response.send_message("PSN is already linked to a Discord account.")
            else:
                psnawp = PSNAWP('YOUR PSN AWP TOKEN') # PSN TOKEN FOR PS API  
                client1 = psnawp.me()
                test = get_random_string(8)

                cursor.execute("SELECT clustername FROM clusterinfo WHERE guild_id = ?", (interaction.guild.id,))
                clustername = cursor.fetchone()

                if clustername:
                    clustername = clustername[0]

                    embed = discord.Embed(description=f"**Go Into PS Settings, \n > Users and Accounts \n > Account \n > Profile \n > 'About/About Me' and set it to **{test}** \n\n\n **It will be checked in 5 minutes**", color=red)
                    await interaction.response.send_message(embed=embed)
                    await asyncio.sleep(300)

                    user_example = psnawp.user(online_id=psn)
                    response = user_example.profile()
                    about_me = response.get('aboutMe', '')
    
                    if about_me == test:
                        print("Success")
                        await interaction.followup.send('Success! PSN has been successfully linked to your Discord account')

                        cursor.execute("INSERT INTO linkedpsn (dcname, psn) VALUES (?, ?)", (interaction.user.mention, psn))
                        db.commit()

                    else:
                        print("Test Failed")
                        await interaction.followup.send(f'{interaction.user.mention} PSN Link **Failed**. Your About Me Was: {about_me}')

                else:
                    print("Cluster name not found for the guild.")
                    await interaction.response.send_message("Cluster name not found for this guild. Please configure it.")
        
    except sqlite3.Error as e:
        print(f"SQLite error: {str(e)}")

async def wl_autocompletion(
    interaction: discord.Interaction,
    current: str
    ) -> typing.List[app_commands.Choice[str]]:
    data = []
    for wl_choice in ['✅ Only Allow Free WL for verified people', '❌ Turn This Off']:
        if current.lower() in wl_choice.lower():
            data.append(app_commands.Choice(name=wl_choice, value=wl_choice))
    return data 

@client.tree.command(name="toggleverifiedwl")
@app_commands.autocomplete(item=wl_autocompletion)
async def veriwl(interaction: discord.Interaction, item: str):
    with sqlite3.connect("freewlbot.db") as db:
        cursor = db.cursor()

        cursor.execute(f"SELECT guild_id FROM freewlverify WHERE guild_id = {interaction.guild.id}")
        data = cursor.fetchone()

        if item == "✅ Only Allow Free WL for verified people":
            if data:
                cursor.execute("UPDATE freewlverify SET question = ? WHERE guild_id = ?", ("Yes", interaction.guild.id))
                await interaction.response.send_message("Verified WL option is enabled.", ephemeral=True)
            else:
                cursor.execute("INSERT INTO freewlverify (question, guild_id) VALUES (?, ?)", ("Yes", interaction.guild.id))
                await interaction.response.send_message("Verified WL option is enabled.", ephemeral=True)

        elif item == "❌ Turn This Off":
            if data:
                cursor.execute("UPDATE freewlverify SET question = ? WHERE guild_id = ?", ("No", interaction.guild.id))
                await interaction.response.send_message("Verified WL option is disabled.", ephemeral=True)
            else:
                cursor.execute("INSERT INTO freewlverify (question, guild_id) VALUES (?, ?)", ("No", interaction.guild.id))
                await interaction.response.send_message("Verified WL option is disabled.", ephemeral=True)

        db.commit()

@tasks.loop(hours=2)
async def update_discord_list():
    global discords

    channel_id = 1172693004046315623  
    original_message_id = 1172694096947724378  

    with sqlite3.connect("freewlbot.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT clustername FROM clusterinfo")
        discords = [row[0] for row in cursor.fetchall() if row[0] is not None]

    guild = client.get_guild(guild_id) #error i cba fixing 
    channel = guild.get_channel(channel_id)

    original_message = await channel.fetch_message(original_message_id)

    embed = discord.Embed(title="Clusters Using ARC :heavy_check_mark:", description="\n <:onlinearc:1131281660588064998> ~ ".join(discords), color = green)
    await channel_id.send(embed=embed)
    

@tasks.loop(hours=1)
async def update_member_count():
    guild = client.get_guild(1125440197149065388)

    total_member_count = sum(guild.member_count for guild in client.guilds)
    total_discord_count = len(client.guilds)

    voice_channelfortotalusers = guild.get_channel(1172698812930855013)
    voice_channelfordiscord = guild.get_channel(1172700367822266428)

    await voice_channelfortotalusers.edit(name=f'Total Users: {total_member_count}')
    await voice_channelfordiscord.edit(name=f'Total Discords: {total_discord_count}')


@client.tree.command(name="tos")
async def tos(interaction:discord.Interaction):
    if interaction.guild_id == 1125440197149065388:
        embed = discord.Embed(description="**ARC INFO/TOS** \nARC is a lightweight tool designed for `ARK:SE` which is **FREE** and can perform simple tasks such as Whitelisting, Banning, PSN/Player Searches and More. \n\n `TOS:` \n > No Racism/Sexism/Homophobic Stuff. \n > Respect Staff, We are providing a free service so any downtime/issues isn't causing any money loss \n > No Advertising Clusters (Or Anything Else) \n > Spamming chat will result in a mute \n\n\n\n <:onlinearc:1131281660588064998> - Feeling Generious?: [Click This](https://paypal.me/voreo)", color = green)
        embed.set_thumbnail(url = "https://cdn.dribbble.com/users/1007527/screenshots/2992564/arc-logo.png")
        iconURL = 'https://i.imgur.com/f4hkXHI.png'
        embed.set_author(name=f"ARC TOS" ,icon_url=iconURL)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("This can only be used in ARC Guild.")


@client.tree.command(name='setupadminlogs', description='Set up admin logs in a channel')
async def setup_admin_logs(interaction, adminlogchannel: str):
    if interaction.guild is None:
        await interaction.response.send_message("This command can only be used in a server.")
        return

    guild_id = interaction.guild.id

    with sqlite3.connect("freewlbot.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT log_channel_id FROM log_channels WHERE guild_id = ?", (guild_id,))
        existing_channel = cursor.fetchone()

        if existing_channel:
            await interaction.response.send_message(f"Admin logs are already set up in {existing_channel[0]}.")
            return

    try:
        with sqlite3.connect("freewlbot.db") as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO log_channels (guild_id, log_channel_id) VALUES (?, ?)", (guild_id, adminlogchannel))
            db.commit()
            await interaction.response.send_message(f"Admin logs will now be sent to {adminlogchannel}.")
    except asyncio.TimeoutError:
        await interaction.response.send_message("Setup timed out. Please run the command again to set up admin logs.")

command_counts = {}

sent_admin_commands = {}

async def find_new_admin_commands(guild_id, file_path):
    new_admin_commands = []

    if guild_id not in command_counts:
        command_counts[guild_id] = {}
        sent_admin_commands[guild_id] = set()

    admin_command_pattern = re.compile(r"(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}).*AdminCmd: (.*)")

    with open(file_path, mode="r") as f:
        for line in f:
            match = admin_command_pattern.search(line)
            if match:
                timestamp, full_command = match.group(1), match.group(2)

                command_identifier = f"{timestamp}_{full_command}"

                if command_identifier not in sent_admin_commands[guild_id]:
                    command_counts[guild_id][command_identifier] = command_counts[guild_id].get(command_identifier, 0) + 1

                    sent_admin_commands[guild_id].add(command_identifier)

    if command_counts[guild_id]:
        grouped_commands = {}
        for command_identifier, count in command_counts[guild_id].items():
            _, full_command = command_identifier.split("_", 1)
            command_name = re.match(r'^\w+', full_command).group()
            grouped_commands.setdefault(command_name, []).append(count)

        for command_name, counts in grouped_commands.items():
            total_count = sum(counts)
            new_admin_commands.append(f"{total_count}x {command_name} used {len(counts)} times")
            print(f"New admin commands found for guild {guild_id}: {new_admin_commands}")

    return new_admin_commands

MAX_EMBED_CHARACTERS = 2048
BUFFER_SIZE = 1000


@tasks.loop(seconds=60)
async def logdaloop():
    try:
        for guild in client.guilds:
            guild_id = guild.id

            try:
                await log_loop(guild_id)
            except Exception as e:
                pass

    except Exception as e:
        pass

async def log_loop(guild_id):
    with sqlite3.connect(db_file) as db:
        cursor = db.cursor()
        cursor.execute("SELECT ntoken FROM clusterinfo WHERE guild_id = ?", (guild_id,))
        nitoken = cursor.fetchone()
        cursor.close()

    if nitoken is None:
        return

    nitoken = nitoken[0]
    a = {"Authorization": f"Bearer {nitoken}"}


    with sqlite3.connect(db_file) as db:
        cursor = db.cursor()
        cursor.execute("SELECT services FROM clusterinfo WHERE guild_id = ?", (guild_id,))
        server_ids = cursor.fetchone()[0]
        if isinstance(server_ids, int):
            server_ids = [str(server_ids)]
        else:
            server_ids = server_ids.split(",")

    connector = TCPConnector(limit=50)  
    async with ClientSession(connector=connector) as ses:
        tasks = []
        for server_id in server_ids:
            tasks.append(download_log(guild_id, server_id, a, ses))

        for task in asyncio.as_completed(tasks):
            try:
                await task
            except Exception as e:
                pass


async def download_log(guild_id, server_id, a, ses):
    try:
        async with ses.get(f'https://api.nitrado.net/services/{server_id}/gameservers', headers=a) as r:
            if r.status != 200:
                return

            json_data = await r.json()
            username = json_data['data']['gameserver']['username']
            game = json_data["data"]["gameserver"]["game"].lower()

            if game == "arkps":
                log_paths = [
                    "arkps/ShooterGame/Saved/Logs/ShooterGame_Last.log",
                    "arkps/ShooterGame/Saved/Logs/ShooterGame.log"
                ]
            else:
                print("ERROR LINE 1605")
                return

            merged_log_lines = []
            for log_path in log_paths:
                async with ses.get(f'https://api.nitrado.net/services/{server_id}/gameservers/file_server/download?file=/games/{username}/noftp/arkps/ShooterGame/Saved/Logs/ShooterGame.log', headers=a) as resp:          
                    data = await resp.json()
                    if resp.status != 200:
                        return

                    json_resp = await resp.json()
                    url = json_resp["data"]["token"]["url"]

                    async with ses.get(url, headers=a) as res:
                        if res.status != 200:
                            return

                        log_lines = await res.text()
                        merged_log_lines.extend(log_lines.splitlines())

            with sqlite3.connect(db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT clustername FROM clusterinfo WHERE guild_id = ?", (guild_id,))
                name = cursor.fetchone()[0]
                folder_name = "ARCASELOGS"
                directory = os.path.join(os.path.dirname(__file__), folder_name, str(guild_id))
                os.makedirs(directory, exist_ok=True)
                file_path = os.path.join(directory, f'{server_id}.ShooterGames.log')

                with open(file_path, mode="w") as f:
                    f.write("\n".join(merged_log_lines))

    except Exception as e:
        pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@tasks.loop(seconds=60)
async def admin_log_loop():
    try:
        with sqlite3.connect("freewlbot.db") as db:
            for guild in client.guilds:
                guild_id = guild.id
                try:
                    await process_admin_commands(guild_id, db)
                except Exception as e:
                    logging.exception(f"Error processing admin commands for guild {guild_id}: {e}")
    except Exception as e:
        logging.exception(f"Error in admin_log_loop: {e}")

async def process_admin_commands(guild_id, db):
    cursor = db.cursor()
    cursor.execute("SELECT services, admin_logging_channel FROM clusterinfo WHERE guild_id = ?", (guild_id,))
    result = cursor.fetchone()

    if result:
        server_ids, admin_log_channel_id_str = result
        if not isinstance(admin_log_channel_id_str, str):
            return
        
        try:
            admin_log_channel_id = int(re.match(r"<#(\d+)>", admin_log_channel_id_str).group(1))
        except (TypeError, AttributeError) as e:
            return

        if isinstance(server_ids, int):
            server_ids = [str(server_ids)]
        else:
            server_ids = server_ids.split(",")

        embeds = []
        for server_id in server_ids:
            folder_name = "/root/ARCASELOGS"
            directory = os.path.join(os.path.dirname(__file__), folder_name, str(guild_id))
            os.makedirs(directory, exist_ok=True)
            file_path = os.path.join(directory, f'{server_id}.ShooterGames.log')

            if os.path.exists(file_path):
                last_processed_timestamp_str = get_last_processed_timestamp(guild_id, server_id)
                last_processed_timestamp = datetime.datetime.strptime(last_processed_timestamp_str, "%Y.%m.%d-%H.%M.%S:%f") if last_processed_timestamp_str else datetime.datetime(1970, 1, 1)

                logging.info(f"Processing server_id: {server_id} with last processed timestamp: {last_processed_timestamp_str}")
                new_log_entries = []
                with open(file_path, "r") as file:
                    log_lines = file.readlines()
                    for log_line in log_lines:
                        logging.info(f"Starting to process file: {file_path} ")
                        logging.info(f"Processing log line: {log_line.strip()}")
                        timestamp_match = re.search(r"\[(\d+\.\d+\.\d+-\d+.\d+.\d+:\d+)\]", log_line)
                        if timestamp_match:
                            timestamp_str = timestamp_match.group(1)
                            log_timestamp = datetime.datetime.strptime(timestamp_str, "%Y.%m.%d-%H.%M.%S:%f")
                            if log_timestamp > last_processed_timestamp:
                                logging.info(f"New command found, processing: {log_line.strip()}")
                                admin_cmd_match = re.search("AdminCmd: ([^ ]+) .*?PlayerName: ([^,]+), ARKID: (\d+), SteamID: (\d+)", log_line)
                                if admin_cmd_match:
                                    command, player_name, ark_id, steam_id = admin_cmd_match.groups()
                                    logging.info(f"Found log entry at {log_timestamp} for command {command} by {player_name}")
                                    formatted_timestamp = format_timestamp_for_discord(log_timestamp)
                                    entry_symbol = ":interrobang:" if command == "gcm" else ""
                                    entry = f"{formatted_timestamp} - {player_name}: {entry_symbol} {command}"
                                    new_log_entries.append(entry)
                                else:
                                    logging.info(f"Skipping already processed command: {log_line.strip()}")

                if new_log_entries:
                    embed = discord.Embed(title="New Admin Commands", description="", color=discord.Color.blue())
                    for entry in new_log_entries:
                        if len(embed.description) + len(entry) < 2048:
                            embed.description += entry + "\n"
                        else:
                            embeds.append(embed)
                            embed = discord.Embed(title="New Admin Commands", description=entry + "\n", color=discord.Color.blue())
                    embeds.append(embed)

                if embeds:
                    admin_log_channel = client.get_channel(admin_log_channel_id)
                    if admin_log_channel:
                        for embed in embeds:
                            logging.info(f"Sending embed with {len(new_log_entries)} new entries to channel ID {admin_log_channel_id}.")
                            await admin_log_channel.send(embed=embed)
                            logging.info("Embed sent successfully.")
                
                if log_lines:
                    last_log_line = log_lines[-1]
                    timestamp_match = re.search(r"\[(\d+\.\d+\.\d+-\d+.\d+.\d+:\d+)\]", last_log_line)
                    if timestamp_match:
                        timestamp_str = timestamp_match.group(1).replace("+00:00", "+0000")
                        last_processed_timestamp = parse_timestamp(timestamp_str)
                        if last_processed_timestamp:
                            update_last_processed_timestamp(guild_id, server_id, last_processed_timestamp)

def format_timestamp_for_discord(dt):
    return f"<t:{int(dt.timestamp())}:F>"

def get_database_cursor():
    db = sqlite3.connect("freewlbot.db")
    return db.cursor()

def update_last_processed_timestamp(guild_id, server_id, timestamp):
    cursor = get_database_cursor()
    cursor.execute("UPDATE admin_command_tracking SET last_processed_timestamp = ? WHERE guild_id = ? AND server_id = ?", (timestamp.strftime("%Y.%m.%d-%H.%M.%S:%f").rstrip('0'), guild_id, server_id))
    if cursor.rowcount == 0:
        cursor.execute("INSERT INTO admin_command_tracking (last_processed_timestamp, guild_id, server_id) VALUES (?, ?, ?)", (timestamp.strftime("%Y.%m.%d-%H.%M.%S:%f").rstrip('0'), guild_id, server_id))
    cursor.connection.commit()

def get_last_processed_timestamp(guild_id, server_id):
    cursor = get_database_cursor()
    cursor.execute("SELECT last_processed_timestamp FROM admin_command_tracking WHERE guild_id = ? AND server_id = ?", (guild_id, server_id))
    result = cursor.fetchone()
    return result[0].rstrip('.000000Z') if result else "1970.01.01-00.00.00:000000"


def parse_timestamp(timestamp_str):
    try:
        return datetime.datetime.strptime(timestamp_str, "%Y.%m.%d-%H.%M.%S:%f")
    except ValueError:
        logging.error(f"Failed to parse timestamp: {timestamp_str}")
        return None

async def send_embed(channel_id, title, description, color):
    channel = client.get_channel(channel_id)
    if channel and description:
        try:
            embed = discord.Embed(title=title, description=description, color=color)
            current_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Sending admin command info to channel: {title} - {description[:50]}")
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending admin command info to channel: {e}")
    else:
        print("No admin command info to send (description is empty)")



FTP_FILE_PATH = '/arkps/ShooterGame/Saved/Config/WindowsServer/GameUserSettings.ini'



@reportbug.error 
async def on_error_report (interaction: discord.Interaction, error: app_commands.AppCommandError): 
     if isinstance(error, app_commands.CommandInvokeError):
        embed1 = discord.Embed(description='Please Ensure You Have Used /setup and Added Your Cluster Name :smile:', color = red)
        await interaction.followup.send(embed=embed1)


@client.event
async def on_error(interaction: discord.Interaction, error: app_commands.CommandInvokeError):
    if isinstance(error, app_commands.CommandInvokeError):
        embed1 = discord.Embed(description='Something Went Wrong, Please Try Again Later.', color = red)
        await interaction.response.send_message(embed=embed1)

@freewl.error
async def on_test_error(interaction: discord.Interaction, error: app_commands.CommandInvokeError):
    if isinstance(error, app_commands.CommandInvokeError):
        embed1 = discord.Embed(description='Please Ensure You Have Setup Using /setup Before Using This! :) \n **If Setup Please Wait 1 minute or Report The Error Using /reportbug**', color = red)
        await interaction.response.send_message(embed=embed1)

@freewl.error
async def on_test_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        embed1 = discord.Embed(description='This command is on cooldown, please try again in {:.2f}s'.format(error.retry_after), color = red)
        await interaction.response.send_message(embed=embed1)

loop.run_until_complete(client.start(TOKEN))
