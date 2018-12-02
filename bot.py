import discord
import requests
import random
import time
import embeds

client = discord.Client()
vote = False


# TODO Passar o bot pra Rewrite
# TODO Comando a praçaénossa
# TODO Jogo de Cartas


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    await client.change_presence(game=discord.Game(name='Merda na sua cara'))
    print('-' * len(client.user.id))


@client.event
async def on_member_join(member):
    canal = client.get_channel("297130716985032714")
    msg = f"{member.mention} Entrou no Clã Do Mosquito, ae caraiou"
    await client.send_message(canal, msg)


@client.event
async def on_member_remove(member):
    canal = client.get_channel("297130716985032714")
    msg = f"{member.mention} Saiu do clã, kkk otário"
    await client.send_message(canal, msg)


@client.event
async def on_error(error):
    print(error)


@client.event
async def on_message(message):
    tempo = f'{message.timestamp:%d-%m-%Y às %H:%M:%S}'
    try:
        if message.author == client.user:
            return
        elif message.content.lower().startswith('$escolha'):
            escolhas = message.content[9:].split(' ')
            escolhido = random.choice(escolhas)
            await client.send_message(message.channel, f'A opção escolhida foi')
            time.sleep(1)
            await client.send_message(message.channel, f'{escolhido}')

        elif message.content.lower().startswith('$wtf'):
            await client.send_file(message.channel, fp='images/wtf.jpg')
            print(f'{tempo} {message.author}: {message.content}')

        elif message.content.lower().startswith('$me'):
            print(f'{tempo} {message.author}: {message.content}')
            emb = discord.Embed(colour=random.randint(0, 0xFFFFFF))
            emb.set_author(name=f'Informações de {message.author.name + message.author.discriminator}')
            emb.set_thumbnail(url=message.author.avatar_url)
            emb.add_field(name=':bust_in_silhouette:| Nome', value=f'```{message.author.name}```')
            emb.add_field(name=':pencil:| Apelido', value=f'```{message.author.nick}```')
            emb.add_field(name=':id:| id', value=f'```{message.author.id}```')
            emb.add_field(name=':robot:| É Bot?', value=f'```{message.author.bot}```'
                          .replace('False', 'Não').replace('True', 'Sim'))
            emb.add_field(name=':alarm_clock:| Criado em',
                          value=f'```{message.author.created_at:%d-%m-%Y às %H:%M:%S}```')
            emb.add_field(name=':large_blue_circle:| Status', value=f'```{message.author.status}```'
                          .replace('dnd', 'Não pertubar').replace('idle', 'Ausente').replace('online', 'Disponível'))
            emb.add_field(name=':calendar:| Entrou no clã em',
                          value=f'```{message.author.joined_at:%d-%m-%Y às %H:%M:%S}```')
            emb.add_field(name=':joystick:| Game',
                          value=f'```{message.author.game}```'.replace('None', 'Nenhum'))
            emb.set_footer(text=f'Pedido por: {message.author.name + message.author.discriminator}',
                           icon_url=message.author.avatar_url)
            await client.send_message(message.channel, embed=emb)

        elif message.content.lower().startswith('$cat'):
            print(f'{tempo} {message.author}: {message.content}')
            main_url = 'http://aws.random.cat/meow'
            cat = requests.get(main_url).json()
            json_cat = cat['file']
            e = discord.Embed(colour=random.randint(0, 0xFFFFFF))
            e.set_image(url=json_cat)
            await client.send_message(message.channel, embed=e)

        elif message.content.lower().startswith('$democracia'):
            print(f'{tempo} {message.author}: {message.content}')
            global opcoes
            opcoes = message.content.split(' ')
            opcoes.remove('$democracia')
            global votou
            votou = []
            global vote
            vote = True
            global votos1, votos2
            votos1 = 0
            votos2 = 0
            await client.send_message(message.channel,
                                      f'Digite $votar 1 para votar em {opcoes[0]}'
                                      f'\nDigite $votar 2 para votar em {opcoes[1]} ')

        elif message.content.lower().startswith('$votar'):
            print(f'{tempo} {message.author}: {message.content}')
            if vote:
                if message.author.name in votou:
                    await client.send_message(message.channel, f'Você já votou, {message.author.mention}')
                else:
                    votou.append(message.author.name)
                    if message.content[7] == '1':
                        votos1 += 1
                        await client.send_message(message.channel, f'+1 voto contado para "{opcoes[0]}"')
                    elif message.content[7] == '2':
                        votos2 += 1
                        await client.send_message(message.channel, f'+1 voto contado para "{opcoes[1]}"')
                    else:
                        await client.send_message(message.channel,
                                                  f'Número de votação inválido {"<@!" + message.author.id + ">"}')
            else:
                await client.send_message(message.channel, 'Nenhuma votação está ocorrendo no momento')

        elif message.content.lower().startswith('$resultados'):
            if vote:
                print(f'{tempo} {message.author}: {message.content}')
                await client.send_message(message.channel, f'Votação encerrada!')
                await client.send_message(message.channel,
                                          f'{votos1} votos para {opcoes[0]}'f'\n{votos2} votos para {opcoes[1]}')
                vote = False
                votos1 = 0
                votos2 = 0
                votou = []
            else:
                await client.send_message(message.channel, 'Nenhuma votação está ocorrendo no momento')

        elif message.content.lower().startswith('$limpar'):
            print(f'{tempo} {message.author}: {message.content}')
            lim = int(message.content.lower()[7:]) + 1
            await client.purge_from(message.channel, limit=lim)
            msg = await client.send_message(message.channel, f'{lim} mensagens limpas')
            time.sleep(3)
            await client.delete_message(msg)

        elif message.content.lower().startswith('$diga'):
            await client.send_message(message.channel, message.content[6:])
            print(f'{tempo} {message.author}: {message.content}')

        elif message.content.lower().startswith('$paz'):
            await client.send_file(message.channel, 'images/paz.jpg')
            print(f'{tempo} {message.author}: {message.content}')

        elif message.content.lower().startswith('$entrar'):
            print(f'{tempo} {message.author}: {message.content}')
            try:
                canal = message.author.voice.voice_channel
                await client.join_voice_channel(canal)
            except discord.errors.InvalidArgument:
                await client.send_message(message.channel, ':dvd: Você prescisa estar em um canal de voz!')

        elif message.content.lower().startswith('$sair'):
            print(f'{tempo} {message.author}: {message.content}')
            try:
                canaldevoz = client.voice_client_in(message.server)
                await canaldevoz.disconnect()
                await client.send_message(message.channel, ":dvd: Desconectado do canal com sucesso!")
            except AttributeError:
                await client.send_message(message.channel, ":dvd: O bot não está conectado em nenhum canal de voz!")

        elif message.content.lower().startswith('$pintao'):
            await client.send_file(message.channel, 'images/pintao.png')
            print(f'{tempo} {message.author}: {message.content}')

        elif message.content.lower().startswith('$felps'):
            await client.send_file(message.channel, 'images/felps.png')
            print(f'{tempo} {message.author}: {message.content}')

        elif message.content.lower().startswith('$ping'):
            msg = await client.send_message(message.channel, '<a:loading:509160083305791488>')
            ms = str(msg.timestamp - message.timestamp)
            await client.edit_message(msg, f'Pong!, `{ms[8:11]}ms`')
            print(f'{tempo} {message.author}: {message.content}')

        elif message.content.lower().startswith('$pergunta'):
            if 'sentido da vida' in message.content.lower():
                await client.send_message(message.channel, '**42**')
            else:
                await client.send_message(message.channel, random.choice(["Sim",
                                                                          "Com certeza",
                                                                          "Talvez",
                                                                          "Eu sei lá porra",
                                                                          "Não"]))
            print(f'{tempo} {message.author}: {message.content}')

        elif message.content.lower().startswith('$help'):
            await client.send_message(message.channel, 'Enviei os comandos na DM')
            await client.send_message(message.author, embed=embeds.help)
            print(f'{tempo} {message.author}: {message.content}')

        elif message.content.lower().startswith('$'):
            embed = discord.Embed(title="Comando não encontrado",
                                  description="Use $help para ver os comandos disponíveis", color=0xff0000)
            embed.set_author(name="IH DEU RUIM", url="https://mosquitao.glitch.me")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/459137918318149635.png?v=1")
            await client.send_message(message.channel, embed=embed)
            print(f'{tempo} {message.author}: {message.content}')
    except Exception as err:
        await client.send_message(message.channel, err)

client.run('NTA4ODA3OTE5ODc0MzQyOTIx.DsEoFQ.2Ziej9nQ4f726yQTWo6oETULTI0')
