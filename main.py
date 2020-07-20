""" Main file to run the bot """
import os
import time
import random
import praw
import prawcore
import aiohttp
import youtube_dl
import discord
import asyncio
from datetime import datetime, timezone, timedelta
from discord.ext import commands
from chanGet import main as getChan
from PIL import Image
from io import BytesIO


bot = commands.Bot(command_prefix='$', case_insensitive=True)
OWNER_ID = int(os.getenv("OWNER_ID"))
REDDIT_ID = os.getenv("REDDIT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
TOKEN = os.getenv("MosquitaoToken")
YTDL_FORMAT_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': './songs/%(extractor)s-%(id)s.%(ext)s',
    'restrictfilenames': False,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': False,
    'verbose': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
YT_DL = youtube_dl.YoutubeDL(YTDL_FORMAT_OPTIONS)
ta_playando = None
song_queue = []


@bot.event
async def on_ready():
    """
    Função para quando o bot iniciar
    """
    print('----------------------------')
    print(f'Bot iniciado {datetime.now(tz=timezone(timedelta(hours=-3)))}')
    print(f'Logado como {bot.user.name}')
    print('----------------------------')
    await bot.change_presence(activity=
                              discord.Game(name=f'bosta na cara de {len(bot.users)} pessoas'))

"""
@bot.event
async def on_command_error(ctx, error):
#   Função para lidar com erros em comandos
    error = getattr(error, 'original', error)
    if hasattr(ctx.command, 'on_error'):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send('Este comando prescisa de algum argumento\n'
                              'Manda um `$help` para ver os comandos')
    if isinstance(error, commands.BadArgument):
        return await ctx.send('Erro no argumento')
    if isinstance(error, commands.CommandNotFound):
        return await ctx.send('Comando não encontrado :/')
    canal = bot.get_user(OWNER_ID)
    return await canal.send(f'O comando `{ctx.command}` invocado por `{ctx.author.name}`\n'
                            f'Gerou o erro: `{type(error)}`\n'
                            f'Args: `{error.args}`\n')
"""

@bot.event
async def on_command(ctx):
    """
    Função para printar quando alguém usar comandos.
    """
    print(f'{datetime.now(tz=timezone(timedelta(hours=-3)))} {ctx.message.author}: {ctx.message.content}')


@bot.event
async def on_member_join(member):
    """
    Função para quando alguém entrar no servidor.
    """
    try:
        canal = bot.get_channel(297130716985032714)
        msg = f"{member.mention} Entrou no Clã Do Mosquito, ae caraiou"
        await canal.send(msg)
    except AttributeError:
        pass


@bot.event
async def on_member_remove(member):
    """
    Função para quando alguém sair do servidor.
    """
    try:
        if member.id == bot.user.id:
            return
        else:
            canal = bot.get_channel(297130716985032714)
            msg = f"{member.name} Saiu do clã, kkk otário"
            await canal.send(msg)
    except AttributeError:
        pass


@bot.command()
async def play(ctx, *, url):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            return await ctx.send("Você precisa estar conectado em um canal de voz.")
    async with ctx.typing():
        os.system("rd /s /q songs") if os.name == "nt" else os.system("rm -rf songs") # Limpa o cache da pasta songs
        song_dl = YT_DL.extract_info(url)
        if song_dl["_type"] == "playlist":
            for song in song_dl['entries']:
                song["ctx"] = ctx
                song["requester"] = ctx.author
                song["song_path"] = f'./songs/{song["extractor"]}-{song["id"]}.{song["ext"]}'
                song["play_source"] = discord.FFmpegPCMAudio(source=song["song_path"])
            song_queue.extend(song_dl["entries"])
            if len(song_dl['entries']) > 1:
                await ctx.send(f"Adicionei `{len(song_dl['entries'])}` musicas na lista.")
        else:
            song_info = song_dl["entries"][0] if song_dl.get("entries") else song_dl
            song_info["ctx"] = ctx
            song_info["requester"] = ctx.author
            song_info["song_path"] = f'./songs/{song_info["extractor"]}-{song_info["id"]}.{song_info["ext"]}'
            song_queue.append(song_info)
        if ctx.voice_client.is_playing():
            return await ctx.send(F"{song_queue[-1]['title']} adicionada à lista.")
        emb = discord.Embed(title=song_queue[-1]["title"], url=song_queue[-1]["webpage_url"], colour=random.randint(0, 0xFFFFFF))
        emb.set_author(name=f"Canal: {song_queue[0]['uploader']}", url=song_queue[-1]["uploader_url"])
        emb.set_thumbnail(url=song_queue[-1]["thumbnail"])
        emb.add_field(name="Duração", value=timedelta(seconds=song_queue[-1]["duration"]), inline=True)
        emb.add_field(name="Pedido por", value=song_queue[-1]["requester"].name, inline=True)
        emb.set_footer(text="Conectado a " + ctx.voice_client.endpoint)
        ctx.voice_client.play(song_queue[-1]['play_source'], after=lambda e: play_next(ctx=ctx))
        global ta_playando
        ta_playando = song_queue[-1]
        await ctx.send(embed=emb)


def play_next(ctx):
    if len(song_queue) > 1:
        global ta_playando
        for i, songa in enumerate(song_queue):
            if songa["song_path"] == ta_playando["song_path"]:
                index = i
                break
        if song_queue[index]["ctx"].voice_client.is_playing(): song_queue[index]["ctx"].voice_client.stop()
        song_queue[index+1]["ctx"].voice_client.play(song_queue[index+1]['play_source'], after=lambda e: play_next(ctx=ctx))
        ta_playando = song_queue[index+1]
        emb = discord.Embed(title=song_queue[index+1]["title"], url=song_queue[index+1]["webpage_url"], colour=random.randint(0, 0xFFFFFF))
        emb.set_author(name=f"Canal: {song_queue[index+1]['uploader']}", url=song_queue[index+1]["uploader_url"])
        emb.set_thumbnail(url=song_queue[index+1]["thumbnail"])
        emb.add_field(name="Duração", value=timedelta(seconds=song_queue[index+1]["duration"]), inline=True)
        emb.add_field(name="Pedido por", value=song_queue[index+1]["requester"].name, inline=True)
        emb.set_footer(text="Conectado a " + song_queue[index+1]["ctx"].voice_client.endpoint)
        asyncio.run_coroutine_threadsafe(song_queue[index+1]["ctx"].send(embed=emb), bot.loop)
        del song_queue[index]


@bot.command(aliases=["queue"])
async def lista(ctx):
    """
    Lista de músicas
    """
    msg = "```css"
    for i, song in enumerate(song_queue):
        msg += f"\n{i} - {song['title']}"
    msg += "\n```"
    await ctx.send(msg)


@bot.command()
async def pause(ctx):
    """
    Pausa a música
    """
    ctx.voice_client.pause()


@bot.command()
async def resume(ctx):
    """
    Resume a música
    """
    ctx.voice_client.resume()


@bot.command(aliases=["skip"])
async def pular(ctx):
    """
    Pula a música
    """
    play_next(ctx)


@bot.command(aliases=['tocando', 'nowplaying', 'tocandoagora'])
async def np(ctx):
    """
    O que está tocando?
    """
    emb = discord.Embed(title=ta_playando["title"], url=ta_playando["webpage_url"], colour=random.randint(0, 0xFFFFFF))
    emb.set_author(name=f"Canal: {ta_playando['uploader']}", url=ta_playando["uploader_url"])
    emb.set_thumbnail(url=ta_playando["thumbnail"])
    emb.add_field(name="Duração", value=timedelta(seconds=ta_playando["duration"]), inline=True)
    emb.add_field(name="Pedido por", value=ta_playando["requester"].name, inline=True)
    emb.set_footer(text="Conectado a " + ta_playando["ctx"].voice_client.endpoint)
    await ctx.send(embed=emb)


@bot.command(aliases=["join"])
async def entrar(ctx):
    """
    Comando para entrar no canal de voz.
    """
    canal_de_voz = ctx.author.voice.channel
    await canal_de_voz.connect()


@bot.command(aliases=["leave", "stop"])
async def sair(ctx):
    """
    Comando para sair do canal de voz.
    """
    if ctx.voice_client is None:
        return await ctx.send("Nem to conectado em lugar nenhum, ta louco?")
    await ctx.voice_client.disconnect()


# Comandos
@bot.command(usage='@alguém')
async def gnomed(ctx, pessoa: discord.Member):
    """
    Gnoma pessoas.
    """
    gnome = 'https://j.gifs.com/rRKn4E.gif'
    emb = discord.Embed(colour=random.randint(0, 0xFFFFFF, ))
    nome = pessoa.nick if pessoa.nick else pessoa.name
    autor = ctx.author.nick if ctx.author.nick else ctx.author.name
    emb.set_author(name=f'{nome} foi gnomado por {autor}!!')
    emb.set_image(url=gnome)
    await ctx.send(embed=emb)


@bot.command()
async def cat(ctx):
    """
    Manda uma foto aleatória de um gato.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get('http://aws.random.cat/meow') as r:
            gato = await r.json()
            json_cat = gato['file']
    emb = discord.Embed(colour=random.randint(0, 0xFFFFFF))
    emb.set_image(url=json_cat)
    await ctx.send(embed=emb)


@bot.command(usage='[Opção 1] [Opção 2]')
async def democracia(ctx, *coisa: str):
    """
    Comando para criar votações democráticas.
    """
    global votos1, votos2, votou, vote, coisas, user_iniciou_vote
    user_iniciou_vote = ctx.author.id
    coisas = []
    votou = []
    vote = True
    votos1 = 0
    votos2 = 0
    for palavra in coisa:
        coisas.append(palavra)
    if len(coisas) != 2:
        if len(coisas) < 2:
            await ctx.send('Este comando precisa de duas opções')
        elif len(coisas) > 2:
            await ctx.send('Este comando suporta apenas duas opções')
    else:
        await ctx.send(f'Digite `$votar 1` para votar em `{coisas[0]}`'
                       f'\nDigite `$votar 2` para votar em `{coisas[1]}` ')


@bot.command()
async def votar(ctx, numero: int):
    """
    Comando para votar em votações criadas pelo $democracia.
    """
    global votos1, votos2
    if vote:
        if ctx.author.name in votou:
            await ctx.send(f'Você já votou, {ctx.message.author.mention}')
        else:
            if numero == 1:
                votos1 += 1
                votou.append(ctx.author.name)
                await ctx.send(f'+1 voto contado para "{coisas[0]}"')
            elif numero == 2:
                votos2 += 1
                votou.append(ctx.author.name)
                await ctx.send(f'+1 voto contado para "{coisas[1]}"')
            else:
                await ctx.send(f'Número de votação inválido {ctx.message.author.mention}')
    else:
        await ctx.send('Nenhuma votação está ocorrendo no momento')


@bot.command()
async def resultados(ctx):
    """
    Comando para mostrar resultados da votação.
    """
    if vote:
        if ctx.author.id == user_iniciou_vote:
            await ctx.send(f'Votação encerrada!')
            await ctx.send(f'{votos1} votos para {coisas[0]}'f'\n{votos2} votos para {coisas[1]}')
        else:
            await ctx.send(f'Apenas quem iniciou a votação pode finalizá-la')
    else:
        await ctx.send('Nenhuma votação está ocorrendo no momento')


@bot.command()
async def limpar(ctx, lim: int):
    """
    Comando para limpar mensagens.
    """
    if lim > 30:
        return await ctx.send('O Limite máximo de mensagens é `30`')
    await ctx.channel.purge(limit=(lim + 1))
    msg = await ctx.send(f'{lim + 1} mensagens limpas')
    time.sleep(3)
    await msg.delete()


@bot.command()
async def pergunta(ctx):
    """
    O bot responde perguntas objetivas (sim ou não).
    """
    if 'sentido da vida' in ctx.message.content.lower():
        await ctx.send('**42**')
    else:
        await ctx.send(random.choice(["Sim",
                                      "Com certeza",
                                      "Talvez",
                                      "Não"]))


@bot.command()
async def rng(ctx, inicio: int, ate: int, dados: int):
    """
    Comando para gerar números aleatórios.
    """
    if dados > 5:
        await ctx.send('O número máximo de dados é `5`')
        return
    soma = 0
    for number in range(1, dados + 1):
        sort = random.randint(inicio, ate)
        soma += sort
        await ctx.send(f'O {number}º numero sorteado foi {sort}')
    if dados > 1:
        await ctx.send(f'A soma desses números é {soma}')


@bot.command()
async def escolha(ctx, *escolhas: str):
    """
    Comando para deixar o bot escolher entre várias opções.
    """
    await ctx.send('E a opção escolhida foi')
    time.sleep(0.5)
    await ctx.send(random.choice(escolhas))


@bot.command(usage="[nome do subreddit]")
async def reddit(ctx, subreddits=None):
    """
    Pega um post aleatório de um subreddit específico ou aleatório
    """
    loop_count = 0
    redd = praw.Reddit(client_id=REDDIT_ID,
                       client_secret=REDDIT_SECRET,
                       user_agent='python/requests:mosquitaobot:1.0 (by /u/davioitu)')
    if subreddits is None:
        sub = redd.random_subreddit(nsfw=False)
    elif str(subreddits).lower() == 'nsfw':
        sub = redd.random_subreddit(nsfw=True)
    else:
        try:
            sub = redd.subreddit(subreddits)
            try:
                sub.quaran.opt_in()
            except prawcore.exceptions.Forbidden:
                pass
            a = sub.random()
            del(a)
        except (prawcore.exceptions.Forbidden, prawcore.exceptions.NotFound):
            await ctx.send("Aparentemente tem algo errado nesse subreddit :/")
            return
    ranpost = sub.random()
    if ranpost is None:
        ranpost = random.choice(list(sub.hot()))
    while ranpost != None:
        ranpost = sub.random() if ranpost is not None else random.choice(list(sub.hot()))
        loop_count += 1
        if ranpost.url.endswith(("jpg", "png", "gif", "jpeg", "bmp")):
            break
        if ranpost.is_self and len(ranpost.selftext) <= 1024:
            emb = discord.Embed(title=ranpost.title, url=ranpost.shortlink)
            emb.add_field(value=ranpost.selftext, name='Texto')
            break
        if loop_count > 10:
            return await ctx.send("Rodei, rodei esse sub e não achei um post que consiga postar bad bad :/")
    emb = discord.Embed(title=ranpost.title, url=ranpost.shortlink)
    if ranpost.is_self:
        emb.add_field(value=ranpost.selftext, name='Texto')
    elif ranpost.url.endswith(("jpg", "png", "gif")):
        emb.set_image(url=ranpost.url)
    author_name = '/u/' + ranpost.author.name
    sub_name = '/r/' + ranpost.subreddit.display_name
    emb.set_author(name=sub_name + ' by ' + author_name)
    await ctx.send(embed=emb)


@bot.command()
async def chan(ctx):
    """
    Manda uma foto aleatória do 4chan.
    """
    async with ctx.channel.typing():
        emb = discord.Embed()
        emb.set_image(url=getChan(1))
        await ctx.send(embed=emb)


@bot.command()
async def ping(ctx):
    """
    Comando para ver a latência do bot.
    """
    msg = await ctx.send('<a:loading:509160083305791488>')
    bot_ms = str(msg.created_at - ctx.message.created_at)
    await msg.edit(content=f'Pong!, `{bot_ms[8:11]}ms`')


@bot.command()
async def emojo(ctx, emoji_name):
    """
    Criação automática de emojis :)
    """
    async with ctx.channel.typing():
        async for message in ctx.message.channel.history(limit=50):
            if message.embeds != []:
                async with aiohttp.ClientSession() as session:
                    async with session.get(message.embeds[0].image.url) as r:
                        img = Image.open(BytesIO(await r.read()))
                imagem = BytesIO()
                img.save(imagem, format="PNG" if img.mode == "RGBA" else "JPEG")
                img = imagem.getvalue()
                break
            if message.attachments:
                last_msg = message
                img = await last_msg.attachments[0].read()
                break
        prin
        emo = await ctx.message.guild.create_custom_emoji(name=emoji_name, image=img)
        await ctx.send(f"Emoji criado com sucesso! {str(emo)}")


@bot.command()
async def dog(ctx):
    """
    Foto aleatória de Doguinho AYAYA
    """
    emb = discord.Embed(colour=random.randint(0, 0xFFFFFF))
    async with aiohttp.ClientSession() as session:
        async with session.get("https://random.dog/woof.json") as r:
            dog = await r.json()
            foto = dog['url']
    emb.set_image(url=foto)
    await ctx.send(embed=emb)


# Comandos de Imagem
@bot.command()
async def zap(ctx):
    """
    Engraçadão pô
    """
    emb = discord.Embed(colour=random.randint(0, 0xFFFFFF))
    emb.set_image(url="https://i.imgur.com/bW8xeTy.jpg")
    await ctx.send(embed=emb)


@bot.command()
async def paz(ctx):
    """
    Dedo do meio = Símbolo de paz
    """
    emb = discord.Embed(colour=random.randint(0, 0xFFFFFF))
    emb.set_image(url="https://i.imgur.com/LfnWoxA.jpg")
    await ctx.send(embed=emb)


@bot.command()
async def felps(ctx):
    """
    Felps.
    """
    emb = discord.Embed(colour=random.randint(0, 0xFFFFFF))
    emb.set_image(url="https://i.imgur.com/NSoXoLG.png")
    await ctx.send(embed=emb)


@bot.command()
async def wtf(ctx):
    """
    Excuse me what the fuck?
    """
    emb = discord.Embed(colour=random.randint(0, 0xFFFFFF))
    emb.set_image(url="https://i.imgur.com/6C0SewT.jpg")
    await ctx.send(embed=emb)


@bot.command()
async def paiva(ctx):
    """
    Punheta.
    """
    emb = discord.Embed(colour=random.randint(0, 0xFFFFFF))
    emb.set_image(url="https://i.imgur.com/iY4MaXu.png")
    await ctx.send(embed=emb)


@bot.command()
async def pintao(ctx):
    """
    Mostra o pintão foda do Alan.
    """
    emb = discord.Embed(colour=random.randint(0, 0xFFFFFF))
    emb.set_image(url="https://i.imgur.com/6MLe4Uw.png")
    await ctx.send(embed=emb)


@bot.command(usage="[algo]")
async def diga(ctx, *, frase):
    """
    Faz o bot dizer algo.
    """
    await ctx.send(frase)


@bot.command(usage="[@alguém]")
async def info(ctx, user: discord.Member):
    """
    Pega informações de um usuário
    """
    emb = discord.Embed(colour=random.randint(0, 0xFFFFFF))
    emb.set_author(name=f'Informações de {user.name + user.discriminator}')
    emb.set_thumbnail(url=user.avatar_url)
    emb.add_field(name=':busts_in_silhouette:| Nome', value=f'```{user.name}```')
    emb.add_field(name=':pencil:| Apelido', value=f'```{user.nick}```'.replace('None', 'Nenhum'))
    emb.add_field(name=':id:| id', value=f'```{user.id}```')
    emb.add_field(name=':robot:| É Bot?', value=f'```{user.bot}```'.replace('False', 'Não').replace('True', 'Sim'))
    emb.add_field(name=':alarm_clock:| Criado em', value=f'```{user.created_at:%d-%m-%Y às %H:%M:%S}```')
    emb.add_field(name=':large_blue_circle:| Status',
                  value=f'```{user.status}```'.replace('dnd', 'Não pertubar').replace('idle', 'Ausente').replace(
                      'online', 'Disponível'))
    emb.add_field(name=':calendar:| Entrou no clã em', value=f'```{user.joined_at:%d-%m-%Y às %H:%M:%S}```')
    if user.activity is not None:
        if user.activity.name == 'Spotify':
            emb.add_field(name=':loud_sound:| Ouvindo', value=f'```{user.activity.title} - {user.activity.artist}```')
        else:
            emb.add_field(name=':joystick:| Game', value=f'```{user.activity.name}```'.replace('None', 'Nenhum'))
    else:
        emb.add_field(name=':joystick:| Game', value='```Nenhum```')
    emb.set_footer(text=f'Pedido por: {ctx.author.name + ctx.author.discriminator}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed=emb)


bot.run(TOKEN)
