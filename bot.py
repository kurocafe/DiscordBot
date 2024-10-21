from typing import Optional
import discord
from discord.ext import commands, tasks
import discord.ui
import random
from datetime import datetime
import time
import json
from os import getenv
from discord.ui.item import Item
import asyncio
import ollama
import requests
import io
from pydub import AudioSegment
import soundfile as sf
import sqlite3 as sql
from dotenv import load_dotenv
load_dotenv()

url = getenv('URL')

DEFAULT_SYSTEM_PROMPT = "あなたは誠実で優秀な日本人のアシスタントです。特に指示が無い場合は、常に日本語で回答してください。2~3文で簡潔に答えてください。もし、答えられない場合は「答えられません」と教えてください。"
modelfile='''
FROM ./Llama-3-ELYZA-JP-8B-q4_k_m.gguf
SYSTEM あなたは誠実で優秀な日本人のアシスタントです。あなたは女性です。あなたの名前は「ミヤコ」です。
TEMPLATE """{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>

{{ .Response }}<|eot_id|>"""
PARAMETER stop "<|start_header_id|>"
PARAMETER stop "<|end_header_id|>"
PARAMETER stop "<|eot_id|>"
PARAMETER stop "<|reserved_special_token"
'''

M_now = datetime.now().strftime('%m')
D_now = datetime.now().strftime('%d')
h_now = datetime.now().strftime('%H')
m_now = datetime.now().strftime('%M')

def GetMonth() -> str:
    return datetime.now().strftime('%m')

def GetDay() -> str:
    return datetime.now().strftime('%d')

def GetHours() ->str:
    return datetime.now().strftime('%H')

def GetMinutes() -> str:
    return datetime.now().strftime('%M')

messages=[
    {'role': 'assistant', 'content': "何でも話してね"}
]

messages_2=[
    {'role': 'system', 'content': f"現在は{GetMonth()}月{GetDay()}日,{GetHours()}時{GetMinutes()}分です。"}
]



ChatCnt = 1
# with open('memory.json', encoding="utf-8") as f:
#     memory = json.load(f)

# messages = memory['memory']['chat_history']


TOKEN=getenv('TOKEN')
kurocafe=getenv('DEVELOPER_ID')
Nate=getenv('USER_ID_1')
Seisan=getenv('USER_ID_2')
TestServer=getenv('SERVER_ID_1')
Cthulhu=getenv('SERVER_ID_2')
TokuWaka=getenv('SERVER_ID_3')
Nakaura=getenv('SERVER_ID_4')
Shorei_friends=getenv('SERVER_ID_5')
kurocafeChat=getenv('CHATROOM_ID')
ChatRoom=getenv('CHANNEL_ID')

dbname = 'Memory.db'
conn = sql.connect(dbname)


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
ollama_client = ollama.AsyncClient()
# モデルを更新する時にだけ実行すればい。
# async def setup_model():
#     await ollama_client.create(model='llama3', modelfile=modelfile)

# asyncio.run(setup_model())


@tasks.loop(seconds=60)
async def loop():
    try:
        with open('list.json', encoding="utf-8") as f:
            schedule = json.load(f)
        M_now = datetime.now().strftime('%m')
        D_now = datetime.now().strftime('%d')
        h_now = datetime.now().strftime('%H')
        m_now = datetime.now().strftime('%M')

        for i in range(len(schedule['Schedule'])):
            # print(schedule['Schedule'][i][0]+'月'+schedule['Schedule'][i][1]+'日, '+schedule['Schedule'][i][2]+'時'+schedule['Schedule'][i][3]+'分')
            if (int(schedule['Schedule'][i][0]) == int(M_now)) and (int(schedule['Schedule'][i][1]) == int(D_now)):
                # print("today!")
                if (int(schedule['Schedule'][i][2]) == 8) and (int(schedule['Schedule'][i][3]) == 0):
                    embed = discord.Embed(
                        title="日赤",
                        color=0x7fffff,
                        description="@everyone \n今日は日赤です！！"
                    )

                    embed.set_footer(
                        text=f"made by {bot.user}",
                        icon_url=bot.user.avatar
                    )
                    await channel.send(embed=embed)
                elif (int(schedule['Schedule'][i][2]) == int(h_now)) and (int(schedule['Schedule'][i][3]) == int(m_now)):
                    print("now!")
                    channel = bot.get_channel(schedule['Schedule'][i][4])
                    embed = discord.Embed(
                        title="日赤",
                        color=0x7fffff,
                        description="@everyone \n日赤の時間です！！"
                    )

                    embed.set_footer(
                        text=f"made by {bot.user}",
                        icon_url=bot.user.avatar
                    )
                    await channel.send(embed=embed)
                    del schedule['Schedule'][i]
                    with open('list.json', mode='w') as f:
                        json.dump(schedule, f, indent=2)
    except Exception as e:
        await send_Exception(e)



@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("Blue Archive"))
    # await ollama_client.create(model='Miyako', modelfile=modelfile)
    # await bot.change_presence(activity=discord.Game("test"))
    print('Logged in as '+bot.user.name)
    cur = conn.cursor()
    table1 = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="persons"').fetchone()
    if table1 is None :        
        cur.execute(
            'CREATE TABLE persons(id INTEGER PRIMARY KEY, name STRING)'
        )
        
    table2 = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="messages"').fetchone()
    if table2 is None:
        cur.execute(
            'CREATE TABLE messages(id INTEGER PRIMARY KEY AUTOINCREMENT, usr_id INTEGER, message STRING)'
        )
    
    # try :
    #     cur.execute(f'INSERT INTO messages(usr_id, message) values(100, "ちんちん")')
    #     conn.commit()
    # except Exception as e:
    #     print(e)
    
    # person = cur.execute('SELECT * FROM persons where id = 100').fetchone()
    # print(person)
    # if person is None :
    #     cur.execute('INSERT INTO persons(id, name) values(100, "Taro")')
    #     conn.commit()
    # cur.execute('INSERT INTO persons(name) values("Hanako")')
    # cur.execute('INSERT INTO persons(name) values("Hiroki")')
    


@bot.slash_command(guild_ids=[Nakaura], description='アラームを設定できます！')
async def alarm(ctx, month, day, hours, minutes):
    try:
        schedule = [month, day, hours, minutes, ctx.channel.id]
        with open('list.json', encoding="utf-8") as f:
            update = json.load(f)
        update['Schedule'] = update['Schedule'] + [schedule]
        with open('list.json', mode='w') as f:
            json.dump(update, f, indent=2)

        embed = discord.Embed(
            title="日赤",
            color=0x7fffff,
            description=f"{month}/{day}, {hours}:{minutes}で予約しました！"
        )
        
        embed.set_footer(
            text=f"made by {ctx.user}",
            icon_url=ctx.user.avatar
        )
        await ctx.respond(embed = embed)
        print(update['Schedule'])
    except Exception as e:
        await send_Exception(e)


@bot.slash_command(guild_ids=[Cthulhu], description = 'botを終了します。')
async def quit(ctx):
    try:
        if ctx.author.id == kurocafe:
            await ctx.respond("終了します。")
            await bot.close()
        else:
            await ctx.respond("権限がありません。")
    except Exception as e:
        await send_Exception(e)
        
@bot.slash_command(guild_ids=[Cthulhu], description = 'チャット履歴をリセットします。')
async def reset(ctx):
    try:
        if ctx.author.id == kurocafe:
            await ctx.respond("リセットしました。")
            del messages[1:]
        else:
            await ctx.respond("権限がありません。")
    except Exception as e:
        await send_Exception(e)


# @bot.event
# async def on_raw_typing(payload):
#     if payload.user_id == Nate:
#         user = bot.get_user(Nate)
#         channel_1 = bot.get_channel(830229442625536034)
#         channel_2 = bot.get_channel(1126561190760431669)
#         await channel_1.send(f"{user.mention} 12300円はよ")
#         await channel_2.send(f"{user.mention} 12300円はよ")
#     else:
#         pass


# @bot.event
# async def on_message(message):
#     try:
#         if message.author.id != bot.user.id:
#             dIndex = message.content.index('d')
#             num1 = int(message.content[:dIndex])
#             num2 = int(message.content[dIndex+1:])
#             diceNumber = []
#             print("check")

#             if num1 == 1:
#                 diceNumber = random.randint(1,num2)
#                 if diceNumber <= 5:
#                     await message.reply(f"{num1}d{num2} → {diceNumber} トリケラトプス！")
#                 elif diceNumber >= 96:
#                     await message.reply(f"{num1}d{num2} → {diceNumber} しょうれい！")
#                 else:
#                     await message.reply(f"{num1}d{num2} → {diceNumber}")
#             elif num1 > 1:
#                 for i in range(0,num1):
#                     diceNumber =  diceNumber + [random.randint(1,num2)]
#                 await message.reply(f"{num1}d{num2} → {diceNumber} > {sum(diceNumber)}")
#                 print("test")
#             else :
#                 await message.reply("400 Bad Request (error code: 50035): Invalid Form Body \nIn content: Must be 2000 or fewer in length.")
#                 await message.channel.send("Fuck you.")
#         else:
#             pass
#     except Exception as e:
#         pass

ALLOWED_CHANNEL_IDS = [
    1252552488431783978,
    178169252033863753,
    1252558399741235220,
    1252558567186370630,
    1256210609192828938,
    1282021983969742981,
    1178169252033863753
]


@bot.event
async def on_message(message):
    try:
        if message.author.id != bot.user.id and (message.channel.id in ALLOWED_CHANNEL_IDS):
            await talk(message.content, message)
        elif message.author.id is not bot.user.id:
            dIndex = message.content.index('d')
            num1 = int(message.content[:dIndex])
            num2 = int(message.content[dIndex+1:])
            diceNumber = []
            print("check")

            if num1 == 1:
                diceNumber = random.randint(1,num2)
                if diceNumber <= 5:
                    await message.reply(f"{num1}d{num2} → {diceNumber} トリケラトプス！")
                elif diceNumber >= 96:
                    await message.reply(f"{num1}d{num2} → {diceNumber} しょうれい！")
                else:
                    await message.reply(f"{num1}d{num2} → {diceNumber}")
            elif num1 > 1:
                for i in range(0,num1):
                    diceNumber =  diceNumber + [random.randint(1,num2)]
                await message.reply(f"{num1}d{num2} → {diceNumber} > {sum(diceNumber)}")
                print("test")
            else :
                await message.reply("400 Bad Request (error code: 50035): Invalid Form Body \nIn content: Must be 2000 or fewer in length.")
                await message.channel.send("Fuck you.")
        else:
            pass

    except Exception as e:
        pass
        # await send_Exception(e)
        # print(e)
    

async def talk(message_content, message):
    usr_message={'role': 'user', 'content': message_content}
    usr_id = message.author.id
    usr_name = message.author
    test = message.author.name
    # print(usr_name)
    # print(test)
    cur = conn.cursor()
    person = cur.execute(f'SELECT * FROM persons where id = {usr_id} AND name = "{usr_name}"').fetchone()
    if person is None :
        cur.execute(f'INSERT INTO persons(id, name) values({usr_id}, "{usr_name}")')
        conn.commit()
    
    try :
        cur.execute(f'INSERT INTO messages(usr_id, message) values(?, ?)',
                    (usr_id, json.dumps(usr_message, ensure_ascii=False)))
        conn.commit()
    except Exception as e:
        # print(f"{json.dumps(usr_message, ensure_ascii=False)}")
        await send_Exception(e)
    
    message_str = cur.execute(f'SELECT message FROM messages WHERE usr_id={usr_id}').fetchall()
    # print(message_str)
    try:
        message_json = [json.loads(s[0]) for s in message_str]
        # print(message_json[-30:])
    except Exception as e:
        await send_Exception(e)
        
    try:
        response = await ollama_client.chat(model='Miyako', messages=message_json[-30:])
    except Exception as e:
        await send_Exception(e)
    # print(response['message']['content'])
    # await message.channel.send(response['message']['content'])
    await message.reply(response['message']['content'])
    try :
        # print(message.guild.voice_client)
        if message.guild.voice_client is not None:
            print("check")
            await tts(response['message']['content'], message)
    except Exception as e:
        pass
        # await send_Exception(e)

    new_message = {'role': 'assistant', 'content': response['message']['content']}
    # print("test")
    try :
        cur.execute(f'INSERT INTO messages(usr_id, message) values(?, ?)',
                    (usr_id, json.dumps(new_message, ensure_ascii=False)))
        conn.commit()
        # print("Miyako")
    except Exception as e:
        print(f"{json.dumps(new_message, ensure_ascii=False)}")
        await send_Exception(e)
    
    
async def talk_2(message_content, message):
    print(message_content + "：せいさん。")
    usr_message={'role': 'user', 'content': message_content}
    messages_2.append(usr_message)
    if 30 < len(messages_2):
        messages_2.pop(1)
    response = await ollama_client.chat(model='Miyako', messages=messages_2)
    print(response['message']['content'])
    await message.channel.send(response['message']['content'])
    print(message.guild.voice_client)
    if message.guild.voice_client is not None:
        print("check")
        await tts(response['message']['content'], message)
    new_message = {'role': 'assistant', 'content': response['message']['content']}
    if 10 < len(messages_2):
        messages_2.pop(1)
    messages_2.append(new_message)
    print(len(messages_2))
    
    
async def tts(text :str, message :discord.Message) -> None:
    print(text)
    params = {
        'text' : text,
        'chara_id' : 0
    }
    response = requests.get(url + '/tts', params=params)
    if response.status_code == 200 :
        print("check2")
        # state = bot.voice_clients.is_playing()
        # print(state)
        file_path = "output.wav"
        if message.guild.voice_client.is_playing():
            print("playing")
        else:
            with open(file_path, "wb") as f:
                print("write")
                f.write(response.content)
            message.guild.voice_client.play(discord.FFmpegPCMAudio("output.wav"))
    else :
        print(f"Failed to retrieve audio. Status code: {response.status_code}")
        await message.channel.send(f"Failed to retrieve audio. Status code: {response.status_code}")


@bot.event
async def on_error(event, *args, **kwargs):
    channel = bot.get_channel(1169104103306182716)
    user = bot.get_user(kurocafe)
    embed = discord.Embed(
        title="ERROR!!",
        color=0xff7f7f,
        description=f"event : {event}, \nargs: {args}, \nkwargs : {kwargs}"        
    )
    await channel.send(embed=embed)
    await user.send(embed=embed)
    print("ERROR!!")


async def send_Exception(txt):
    channel = bot.get_channel(1169104103306182716)
    user = bot.get_user(kurocafe)
    embed = discord.Embed(
        title="Exception!!",
        color=0xff7f7f,
        description=f"{txt}"
    )
    await channel.send(embed=embed)
    await user.send(embed=embed)


class SelectChara(discord.ui.View):
    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)
        
    
    @discord.ui.select(
        placeholder="キャラクターを選んでください．", 
        options=[
            discord.SelectOption(label="小鳥遊 心優", value="0"),
            discord.SelectOption(label="小鳥遊 千", value="1"),
            discord.SelectOption(label="九十三 椿妃", value="2"),
            discord.SelectOption(label="絵馬 結月希", value="3"),
            discord.SelectOption(label="東雲 美凪", value="4"),
            discord.SelectOption(label="神々 希", value="5"),
            discord.SelectOption(label="伊集院 誡", value="6"),
        ]
    )

    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        with open('cs.json', encoding="utf-8") as f:
            url = json.load(f)
        await interaction.response.send_message(content=url["url"][int(select.values[0])])


@bot.slash_command(guild_ids=[Cthulhu, TokuWaka])
async def cs(ctx):
    try:
        view = SelectChara()
        await ctx.respond("キャラクターを選んでください．", view=view)
    except Exception as e:
        await send_Exception(e)


@bot.slash_command(guild_ids=[Cthulhu], description ='send pic')
async def huohuo(ctx):
    try:
        with open('list.json', encoding="utf-8") as f:
            Pic = json.load(f)
        await ctx.respond(file=discord.File(Pic["Huohuo"][random.randint(0, len(Pic["Huohuo"])-1)]))
    except Exception as e:
        await send_Exception(e)


@bot.slash_command(guild_ids=[Cthulhu], description='今日のご飯は？')
async def lunch(ctx):
    try:
        with open('list.json', encoding="utf-8") as f:
            list = json.load(f)

        embed = discord.Embed(
            title="今日のご飯は？",
            color=0x7fffff,
            description=list["Lunch"][random.randint(0, len(list["Lunch"])-1)]
        )

        embed.set_author(
            name=bot.user,
            icon_url=bot.user.avatar
        )
        
        embed.set_footer(
            text=f"made by {ctx.user}",
            icon_url=ctx.user.avatar
        )
        await ctx.respond(embed = embed)
        # await ctx.respond(f"{ctx.author.mention} "+list["Lunch"][random.randint(0, len(list["Lunch"])-1)])
    except Exception as e:
        await send_Exception(e)

@bot.slash_command(guild_ids=[Cthulhu, Shorei_friends], description ='ボイスチャンネルに参加します。')
async def join(ctx):
    try:
        if ctx.author.voice is None:
            await ctx.respond("あなたはボイスチャンネルに接続していません。")
            
        else :
            await ctx.author.voice.channel.connect()
            await ctx.respond("接続しました。")
    
    except Exception as e:
        await send_Exception(e)
        
        
@bot.slash_command(guild_ids=[Cthulhu, Shorei_friends], description ='ボイスチャンネルから退出します。')
async def leave(ctx):
    try:
        if ctx.guild.voice_client is None:
            await ctx.respond("ボイスチャンネルに接続していません。")
            
        else :
            await ctx.guild.voice_client.disconnect()
            await ctx.respond("切断しました。") 
    
    except Exception as e:
        await send_Exception(e)
        

@bot.slash_command(guild_ids=[Cthulhu, TokuWaka], description = '色々試すときに使うよ')
async def test(ctx):
    try:
        embed = discord.Embed(
            title="Test Embed", 
            color=0x7fffff,
            description=f"Example Embed",
            url="https://cdn.discordapp.com/attachments/830229442625536034/1243559479367176245/15.jpg?ex=6653e4c4&is=66529344&hm=5d6297a1227f99b9d85e697175616932f771e40f966469bbf1f73b5206cd8688&",
            thumbnail="https://cdn.discordapp.com/attachments/830229442625536034/1243559479367176245/15.jpg?ex=6653e4c4&is=66529344&hm=5d6297a1227f99b9d85e697175616932f771e40f966469bbf1f73b5206cd8688&"
        )
        
        embed.set_author(
            name=bot.user,
            icon_url=bot.user.avatar
        )
        
        embed.set_image(
            url="https://media.discordapp.net/attachments/840253065781444628/1238875504178761830/Untitled82_20240505010106.png?ex=6653fdf9&is=6652ac79&hm=db40955ebe6727063df2a0ccddd15c7ee212af51e1206db6f41a25926d9ae5c3&=&format=webp&quality=lossless&width=263&height=350"
        )
        
        # embed.set_field_at(index=1, name="field_1", value="value_1")
        # embed.set_field_at(name="field_2", value="value_2")
        
        embed.set_footer(
            text=f"made by {ctx.user}",
            icon_url=ctx.user.avatar
        )

        
        await ctx.respond(embed = embed)
    except Exception as e:
        await send_Exception(e)


# loop.start()
bot.run(TOKEN)