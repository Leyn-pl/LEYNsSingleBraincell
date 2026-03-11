import disnake as ds
from disnake.ext import commands
import strings as ss
from datetime import *
import time
import random

# Globals
skillChannel = 1476536285425438781
skillsLoaded = {}
lastChangedStatus: datetime = None

async def fetchSkills(bot: commands.InteractionBot, inter: ds.ApplicationCommandInteraction = None):
    global skillsLoaded
    try:
        message: ds.Message = None
        ctr = 0
        skillsLoaded.clear()
        async for message in bot.get_channel(skillChannel).history():
            name = message.content.split('\n')[0].strip(' #*')
            skillsLoaded.update({name: message.content})
            ctr += 1
        log(f'Загружено приёмов: {ctr} <<< {inter.author.name if inter else None}', 'skills')
        if inter:
            await inter.response.send_message(f'Загружено приёмов: {ctr}.', ephemeral=True)
    except Exception as e:
        log(f'Ошибка при загрузке приёмов: {e}', 'skills.error')
        if inter:
            await inter.response.send_message(f'Ошибка при загрузке приёмов.', ephemeral=True)

async def setActivity(bot: commands.InteractionBot, inter: ds.ApplicationCommandInteraction = None):
    global lastChangedStatus
    if inter and lastChangedStatus:
        timediff = (datetime.now() - lastChangedStatus).total_seconds()
        if timediff < 15*60:
            await inter.response.send_message(ss.statusChangeCooldown, ephemeral=True)
            return
    lastChangedStatus = datetime.now()
    i = random.randrange(len(ss.status))
    await bot.change_presence(activity=ds.CustomActivity(
        name = ss.status[i]
    ))
    log(f'Установлен статус {i+1}/{len(ss.status)}', 'status')
    if inter:
        await inter.response.send_message(f'Установлен статус {i+1}.')

def log(txt: str, source: str = ''):
    if source: source = f'.{source}'
    print(f'[L{source}] {time.strftime('%H:%M:%S')} >>> {txt}')

def bootLog(bot: commands.Bot):
    log([command.name for command in bot.slash_commands], 'boot')

def genCmdList(bot: commands.Bot):
    out = []
    for cmd in sorted(list(bot.slash_commands), key=lambda x: x.name):
        args = f'*{ss.cmdArgs[cmd.name]}* ' if cmd.name in ss.cmdArgs else ''
        out.append(f'**/{cmd.name}** {args}- {cmd.description}')
    return '\n\n'.join(out)

def throwDice(code: str):
    minmax = code.split('-')
    random.seed()
    return random.randint(int(minmax[0]), int(minmax[1]))

async def deleteMessage(message: ds.Message):
    try:
        await message.delete()
        log(f'Сообщение в #{message.channel.name} удалено по реакции.', 'event')
    except Exception as e:
        log(str(e), 'event.error')

# Commands
async def help(inter: ds.ApplicationCommandInteraction, bot: commands.Bot):
    embed = ds.Embed(
        title = ss.botName,
        description = ss.help,
        color = ss.color
    )
    embed.add_field(
        name = 'Список команд',
        value = genCmdList(bot)
    )
    embed.set_author(
        name = 'leyn1092',
        url = ss.link,
        icon_url = bot.get_user(ss.devid).avatar.url
    )
    embed.set_thumbnail(
        url = bot.user.avatar.url
    )
    await inter.response.send_message(embeds=[embed])

async def coin(inter: ds.ApplicationCommandInteraction):
    random.seed()
    land = random.choice(['Орёл!', 'Решка!'])
    user = inter.author.display_name
    bottomtext = ss.bet if random.random() < 0.1 else ''
    await inter.response.send_message(f'**{user}** бросает монетку...')
    time.sleep(1)
    await inter.edit_original_response(f'**{user}** бросил монетку:\n## `{land}`{bottomtext}')

""" Старый кубик
async def dice(inter: ds.ApplicationCommandInteraction, sides: int):
    random.seed()
    result = random.randint(1, sides)
    user = inter.author.display_name
    if result < 10 and sides >= 10:
        result = f' {result} '
    else:
        result = f'{result}'
    bottomtext = ss.bet if result == 1 else ''
    await inter.response.send_message(f'**{user}** бросает D{sides}...')
    time.sleep(1)
    await inter.edit_original_response(f'**{user}** бросил D{sides}:\n## `{result}`{bottomtext}')
"""
# Для NRPC
async def dice(inter: ds.ApplicationCommandInteraction, code: str):
    try:
        result = throwDice(code)
    except ValueError:
        await inter.response.send_message(ss.invalidDiceFormat, ephemeral=True)
        return
    user = inter.author.name
    log(f'{code} -> {result} <<< {user}', 'dice')
    await inter.response.send_message(f'(**{result}**)\n-# // {code}, запросил {user}')

async def clash(inter: ds.ApplicationCommandInteraction, multicode: str):
    code1, code2 = multicode.split(' ')
    try:
        a, b = throwDice(code1), throwDice(code2)
    except ValueError:
        await inter.response.send_message(ss.invalidDiceFormat, ephemeral=True)
        return
    user = inter.author.name
    diff = abs(a - b)
    if a > b:
        winner = f'Левый побеждает с разницей **{diff}**'
    elif b > a:
        winner = f'Правый побеждает с разницей **{diff}**'
    else:
        winner = 'Ничья'
    log(f'{code1}, {code2} -> {a}, {b} <<< {user}', 'dice')
    await inter.response.send_message(f'(**{a}** vs **{b}**: {winner})\n-# // {code1} vs {code2}, запросил {user}')

async def rand(inter: ds.ApplicationCommandInteraction, a: int, b: int):
    random.seed()
    user = inter.author.display_name
    if b < a:
        a, b = b, a
    result = random.randint(a, b)
    bottomtext = ss.bet if result == a else ''
    await inter.response.send_message(f'**{user}** запросил случайное число **[{a}, {b}]**:\n## `{result}`{bottomtext}')

async def length(inter: ds.ApplicationCommandInteraction, user: ds.User):
    random.seed(user.id * (datetime.now() - datetime(1984,1,1)).days)
    result = random.randint(10, 25)
    if result == 25: result += random.randint(1, 10)
    random.seed()
    username = user.display_name
    if result < 16:
        bottomtext = random.choice(ss.Length.small)
    elif result < 25:
        bottomtext = random.choice(ss.Length.medium)
    elif result < 35:
        bottomtext = random.choice(ss.Length.huge)
    else:
        bottomtext = '@_@'
    await inter.response.send_message(f'Длина **{username}**:\n## `{result}см`\n-# {bottomtext}')

async def ship(inter: ds.ApplicationCommandInteraction, user1: ds.User, user2: ds.User):
    random.seed()
    if not user1:
        user1 = random.choice(inter.guild.members)
    if not user2:
        user2 = random.choice(inter.guild.members)
    random.seed(user1.id * user2.id * (datetime.now() - datetime(1984,1,1)).days)
    result = random.randint(1, 100)
    random.seed()
    if ss.botid in [user1.id, user2.id]:
        bottomtext = random.choice(ss.Love.me)
    elif user1.bot or user2.bot:
        bottomtext = random.choice(ss.Love.bot)
    elif result < 35:
        bottomtext = random.choice(ss.Love.low)
    elif result < 70:
        bottomtext = random.choice(ss.Love.medium)
    else:
        bottomtext = random.choice(ss.Love.high)
    user1, user2 = user1.display_name, user2.display_name
    await inter.response.send_message(f'Пара **{user1}** + **{user2}**:\n## Совместимость: `{result}%`\n-# {bottomtext}')

async def ping(inter: ds.ApplicationCommandInteraction):
    tobot = (datetime.now().astimezone(timezone.utc) - inter.created_at.astimezone(timezone.utc)).microseconds // 1000
    await inter.response.send_message(f'**Пинг**: `{tobot}мс`')

async def searchSkills(inter: ds.ApplicationCommandInteraction, codes: list[str]):
    if not skillsLoaded:
        await inter.response.send_message(ss.noSkillsLoaded, ephemeral=True)
    if len(codes[0]) < 3:
        await inter.response.send_message(ss.invalidSkillSearch, ephemeral=True)
        return
    out = []
    for code in codes:
        if len(code) < 3:
            continue
        for skill in skillsLoaded.keys():
            if code.lower() in skill.lower():
                out.append(skillsLoaded[skill])
    if not out:
        await inter.response.send_message(ss.skillsNotFound, ephemeral=True)
        return
    await inter.response.send_message('\n'.join(out), ephemeral=True)