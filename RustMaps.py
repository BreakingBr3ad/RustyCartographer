import requests
import discord
import json
import time
import os.path
import a2s
import monumentsDict
from requests.api import post

with open("config.json") as json_data_file:
    data = json.load(json_data_file)

discordToken = data["discordToken"]
RustMapToken = data["rustmapToken"]
Header = {"accept": "application/json","X-API-Key":RustMapToken}
rustMapLink = "https://rustmaps.com/api/v2/maps/"
client = discord.Client()
day = time.strftime("%m/%d")
server = []
    
def generateMap(size,seed,staging,barren):
    postRequest = requests.post(rustMapLink+str(seed)+"/"+str(size)+"?staging="+staging+"&barren="+barren, headers = Header)
    requestJson = postRequest.json()
    if postRequest.status_code == 409:
        return 409
    else:
        return requestJson["mapId"]

def writetoFile(keyData,size,seed):
    filename = f"{size}_{seed}"
    with open(f'{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(keyData, f, ensure_ascii=False, indent=4)

def getMap(size,seed,staging,barren):
    
    getRequest = requests.get(rustMapLink+str(seed)+"/"+str(size)+"?staging="+staging+"&barren="+barren, headers = Header)
    if getRequest.status_code != 404:
        imageKey = getRequest.json()
        try:
            writetoFile(imageKey,size,seed)
        except Exception as e: print (e)
        if "currentState" in imageKey:
            return ("Map is still generating. Please allow roughly 5 minutes!")

        return imageKey["url"]
    else:
        failMessage = "Map does not exist! Send generate [size] [seed] to generate a map!"
        return failMessage

def getMapbyID(mapID):
    getRequest = requests.get(rustMapLink+str(mapID), headers = Header)
    imageKey = getRequest.json()
    try:
        writetoFile(imageKey,imageKey["size"],imageKey["seed"])
    except Exception as e: print (e)
    keyLength = (len(imageKey))
    if keyLength == 1:
        return imageKey
    else:
        return imageKey

def getServerSeed(url,port):
    serverAddr = (url,port)
    serverResponse = a2s.rules(serverAddr)
    #print (serverResponse)
    server.append(day)
    server.append(serverResponse["url"])
    server.append(serverResponse["world.size"])
    server.append(serverResponse["world.seed"])
    sizeseed = [server[2],server[3]]
    getRequest = requests.get(rustMapLink+str(serverResponse["world.seed"])+"/"+str(serverResponse["world.size"])+"?staging=false&barren=false", headers = Header)
    if getRequest.status_code != 404:
        imageKey = getRequest.json()
        try:
            writetoFile(imageKey,sizeseed[0],sizeseed[1])
            return sizeseed
        except Exception as e: print (e)
    else:
        sizeseed.append("Fail")
        return sizeseed
    serverAddr=tuple()
    sizeseed.clear()

def checkMonuments(size,seed):
    with open(f'{size}_{seed}.json', 'r') as monumentslist:
        data = monumentslist.read()
    obj = json.loads(data)
    mapImg = obj['imageUrl']
    mapIconImg = obj['imageIconUrl']
    mapPage = obj['url']
    monumentsDict.dict['imageUrl'] = mapImg
    monumentsDict.dict['imageIconUrl'] = mapIconImg
    monumentsDict.dict['url'] = mapPage
    for i in obj['monuments']:
        for j in monumentsDict.monuments:
            if i['monument'] == j:
                monumentsDict.dict[f'{j}'] = '✅'
    return monumentsDict.dict

def sendEmbed(size,seed):
    monumentsEmbed = checkMonuments(size,seed)
    embed=discord.Embed(color=0xFF5733, title = f'Size: {size} | Seed: {seed}', url = monumentsEmbed['url'], description = (f'Airfield: {monumentsEmbed["Airfield"]}\nBandit Town: {monumentsEmbed["Bandit_Town"]}\n"Excavator: {monumentsEmbed["Excavator"]}\nLarge Harbor: {monumentsEmbed["Harbor_Large"]}\nSmall Harbor: {monumentsEmbed["Harbor_Small"]}\nJunkyard: {monumentsEmbed["Junkyard"]}\nLaunch Site: {monumentsEmbed["Launch_Site"]}\nLighthouse: {monumentsEmbed["Lighthouse"]}\nMilitary Base A: {monumentsEmbed["Military_Base_A"]}\nMilitary Base B: {monumentsEmbed["Military_Base_B"]}\nMilitary Base C: {monumentsEmbed["Military_Base_C"]}\nMilitary Base D: {monumentsEmbed["Military_Base_D"]}\nMilitary Tunnels: {monumentsEmbed["Military_Tunnels"]}\nOutpost: {monumentsEmbed["Outpost"]}\nPowerplant: {monumentsEmbed["Powerplant"]}\nSatellite Dish: {monumentsEmbed["Satellite_Dish"]}\nSewer Branch: {monumentsEmbed["Sewer_Branch"]}\nThe Dome: {monumentsEmbed["Sphere_Tank"]}\nTrainyard: {monumentsEmbed["Trainyard"]}\nWater Treatment: {monumentsEmbed["Water_Treatment"]}'))
    #print (monumentsEmbed)
    #print (type(monumentsEmbed))
    embed.set_author(name = "Creator: Bread", icon_url="https://i.imgur.com/cUafKbf.png")
    embed.set_footer(text="Powered by Rustmaps.com")
    embed.set_image(url=str(monumentsEmbed['imageIconUrl']))
    return embed

def mapGenErrorEmbed():
    embed=discord.Embed(color=0xFF5733,title="Map Still Generating",description="\nPlease allow 5 minutes for generation to complete")
    embed.set_thumbnail(url='https://i.pinimg.com/originals/b3/b5/3d/b3b53d07fa0c70526c91494e4cbd9491.gif')
    embed.set_author(name = "Creator: Bread", icon_url="https://i.imgur.com/cUafKbf.png")
    embed.set_footer(text="Powered by Rustmaps.com")
    return embed


def limitExceedEmbed():
    embed=discord.Embed(color=0xFF5733,title="Limit Exceeded",description="Seed exceeds integer limit of 2147483647")
    embed.set_author(name = "Creator: Bread", icon_url="https://i.imgur.com/cUafKbf.png")
    embed.set_footer(text="Powered by Rustmaps.com")
    return embed

def helpEmbed():
    embed=discord.Embed(color=0xFF5733)
    embed.set_thumbnail(url='https://i.imgur.com/9tSDy4U.png')
    embed.set_author(name = "Creator: Bread", icon_url="https://i.imgur.com/cUafKbf.png")
    embed.add_field(name="Get the mapID for generating. If it's already generated will link the page", value="```$mapid [mapID]```", inline=False)
    embed.add_field(name="Generate a map based on size, seed, and true/false for staging and barren. Omit for false", value="```$generate [size] [seed] [staging?] [barren?]```", inline=False)
    embed.add_field(name="Get the map based on size, seed, and true/false for staging and barren. Omit for false", value="```$map [size] [seed] [staging?] [barren?]```", inline=False)
    embed.add_field(name="Get the size, seed and map with a servers url and port", value="```$server [url] [port] or [url:port]```", inline=False)
    embed.set_footer(text="Powered by Rustmaps.com")
    return embed
@client.event
async def on_ready():
    print("Login Successful")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if '$' in message.content:
        ##print (len(message.content))
        msgText = message.content
        splitMsgText = msgText.split()
        if 'help' in message.content.lower():
            embed=helpEmbed()
            await message.channel.send(embed=embed)
        elif 'mapid' in message.content.lower():
            MapID = splitMsgText[1]
            try:
                mapImage = getMapbyID(MapID)
                #print ("FUCKER",mapImage)
                await message.add_reaction('🗺️')
                if 'url' not in mapImage:
                    embed=mapGenErrorEmbed()
                    await message.channel.send(embed=embed)
                else:
                    embed = sendEmbed(mapImage["size"],mapImage["seed"])
                    await message.channel.send(embed=embed)
            except Exception as e: print (e)
        elif 'generate' in message.content.lower():
            size = splitMsgText[1]
            seed = splitMsgText[2]
            #print (size)
            #print (seed)
            if int(seed) > 2147483647:
                embed=limitExceedEmbed()
                await message.channel.send(embed=embed)
                #print ("Exceeds 2147483647 limit")
            else:
                embed=discord.Embed(color=0xFF5733)
                embed.set_footer(text="Powered by Rustmaps.com")
                embed.set_author(name = "Creator: Bread", icon_url="https://i.imgur.com/cUafKbf.png")
                embed.set_thumbnail(url='https://i.pinimg.com/originals/b3/b5/3d/b3b53d07fa0c70526c91494e4cbd9491.gif')
                if len(splitMsgText) == 3:
                    staging = "false"
                    barren = "false"
                else:
                    staging = splitMsgText[3]
                    barren = splitMsgText[4]
                try:
                    mapID = generateMap(size,seed,staging,barren)
                    await message.add_reaction('🗺️')
                    if mapID == 409:
                        try:
                            mapImage = getMap(size,seed,staging,barren)   
                            await message.add_reaction('🗺️')
                            if "https" in mapImage:
                                embed=sendEmbed(size,seed)
                                await message.channel.send(embed=embed)
                            else: 
                                embed=mapGenErrorEmbed()
                                await message.channel.send(embed=embed)
                        except Exception as e: 
                            print (e)
                            await message.channel.send("")
                            embed = sendEmbed(size,seed)
                            await message.channel.send(embed=embed)
                            getMap(size,seed)
                    else:
                        embed.add_field(name="Request received",value=f"Map is generating. Retrieve map using: ```$mapid {mapID}```", inline=True)
                        #await message.channel.send("Map ID: "+mapID)
                        await message.channel.send(embed=embed)
                except Exception as e: print (e)   
        elif 'map' in message.content.lower():
            size = splitMsgText[1]
            seed = splitMsgText[2]
            if int(seed) > 2147483647:
                embed=discord.Embed(color=0xFF5733,title="Limit Exceeded",description="Exceeds integer limit of 2147483647")
                embed.set_author(name = "Creator: Bread", icon_url="https://i.imgur.com/cUafKbf.png")
                embed.set_footer(text="Powered by Rustmaps.com")
                await message.channel.send(embed=embed)
                #print ("Exceeds 2147483647 limit")
            else:
                if len(splitMsgText) == 3:
                    staging = "false"
                    barren = "false"
                else:
                    staging = splitMsgText[3]
                    barren = splitMsgText[4]
                try:
                    mapImage = getMap(size,seed,staging,barren)   
                    await message.add_reaction('🗺️')
                    if "https" in mapImage:
                        embed=sendEmbed(size,seed)
                        await message.channel.send(embed=embed)
                    else: 
                        embed=discord.Embed(color=0xFF5733)
                        embed.set_author(name = "Creator: Bread", icon_url="https://i.imgur.com/cUafKbf.png")
                        embed.set_footer(text="Powered by Rustmaps.com")
                        embed.add_field(name="Alert",value=mapImage)
                        await message.channel.send(embed=embed)
                except Exception as e: 
                    print (e)
                    await message.channel.send("")
        elif 'server'  in message.content.lower():
            if ':' in message.content.lower():
                ColonMsgText = splitMsgText[1].split(':')
                url = ColonMsgText[0]
                port = ColonMsgText[1]
            else:
                url = splitMsgText[1]
                port = splitMsgText[2]
            serverSizeSeed = getServerSeed(str(url),int(port))
            if len(serverSizeSeed) == 3:
                mapID = generateMap(serverSizeSeed[0],serverSizeSeed[1],'false','false')
                embed=discord.Embed(color=0xFF5733,url = server[1],title = f"Size: {serverSizeSeed[0]} Seed: {serverSizeSeed[1]}",description=f"Map does not exist! Please allow around 5 minutes for generation. \n\n{mapID}")
                #embedNew=discord.Embed(color=0xFF5733, title = "Alert",description=f"Map is still generating! Please allow around 5 minutes. \n{mapID}")
                embed.set_footer(text="Powered by Rustmaps.com")
                embed.set_author(name = "Creator: Bread", icon_url="https://i.imgur.com/cUafKbf.png")
                await message.channel.send(embed=embed)
            else:
                embed = sendEmbed(serverSizeSeed[0],serverSizeSeed[1])
                await message.channel.send(embed=embed)
            server.clear()
            serverSizeSeed.clear()
        else: 
            embed=helpEmbed()
            await message.channel.send(embed=embed)

client.run(discordToken)
