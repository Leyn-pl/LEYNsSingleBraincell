# SINGE BRAINCELL by LEYN1092
import asyncio

import disnake as ds
from disnake.ext import commands
import features as f
import battleUI as b
import time

# SETUP
with open("TOKEN.txt") as file:
    TOKEN = file.readline()

command_sync_flags = commands.CommandSyncFlags.all()
command_sync_flags.sync_commands_debug = False

bot = commands.InteractionBot(
    test_guilds=[1331297072980430898],
    command_sync_flags=command_sync_flags,
    intents=ds.Intents.all()
)

# EVENTS
@bot.event
async def on_connect():
    print('[RUN] Бот запущен')
    f.bootLog(bot)
    # Подождать, пока загрузится канал с приёмами (гигакостыль)
    for i in range(5):
        try:
            bot.get_channel(1476536285425438781).history(limit=1)
            break
        except:
            await asyncio.sleep(3)
    else:
        f.log('Не удалось прочитать канал с приёмами.', 'boot')
    await f.fetchSkills(bot)
    await f.setActivity(bot)
@bot.event
async def on_reaction_add(reaction: ds.Reaction, user: ds.User):
    if reaction.emoji == '❌' and reaction.message.author.id == bot.user.id:
        await f.deleteMessage(reaction.message)

# SLASH COMMANDS
# хелп
@bot.slash_command(name='хелп', description='Информация о боте и список команд')
async def help(inter):
    await f.help(inter, bot)
# монетка
@bot.slash_command(name='монетка', description='Бросить монетку')
async def coin(inter):
    await f.coin(inter)
# кубик
""" - старый кубик
@bot.slash_command(name='кубик', description='Бросить кубик')
async def dice(inter):
    pass
@dice.sub_command(name='д4', description='Четёрыхгранный')
async def d4(inter):
    await f.dice(inter, 4)
@dice.sub_command(name='д6', description='Шестигранный')
async def d6(inter):
    await f.dice(inter, 6)
@dice.sub_command(name='д8', description='Восьмигранный')
async def d8(inter):
    await f.dice(inter, 8)
@dice.sub_command(name='д10', description='Десятигранный')
async def d10(inter):
    await f.dice(inter, 10)
@dice.sub_command(name='д12', description='Двенадцатигранный')
async def d12(inter):
    await f.dice(inter, 12)
@dice.sub_command(name='д20', description='Двадцатигранный')
async def d20(inter):
    await f.dice(inter, 20)
@dice.sub_command(name='д100', description='Круглый?')
async def d100(inter):
    await f.dice(inter, 100)
# рандом
@bot.slash_command(name='ранд', description='Получить случайное число от 1 до A или от A до B')
async def rand(inter, a: int, b: int = 1):
    await f.rand(inter, a, b)
# длина
@bot.slash_command(name='длина', description='Узнать, сколько см у пользователя')
async def length(inter, user: ds.User):
    await f.length(inter, user)
"""
# шип
@bot.slash_command(name='шип', description='Зашипперить двух пользователей. Случайных, если не указаны')
async def ship(inter, user1: ds.User = None, user2: ds.User = None):
    await f.ship(inter, user1, user2)
# пинг
@bot.slash_command(name='пинг', description='Узнать пинг до бота')
async def ping(inter):
    await f.ping(inter)
## Для NRPC
# консоль
@bot.slash_command(name='debug', description='Выполнить код внутри логики РП боя. Только для разработчика')
@commands.default_member_permissions(administrator=True)
async def debug(inter, cmd: str):
    await b.debug(inter, cmd)
# зареролить статус
@bot.slash_command(name='status', description='Сменить статус бота на случайный.')
async def status(inter):
    await f.setActivity(bot, inter)
# заного загрузить приёмы
@bot.slash_command(name='обновить_приёмы', description='Обновить список приёмов')
async def fetchSkills(inter):
    await f.fetchSkills(bot, inter)
# 1 кубик
@bot.slash_command(name='к', description='Бросить 1 кубик')
async def dice(inter, кубик: str):
    await f.dice(inter, кубик)
# 2 кубика
@bot.slash_command(name='клеш', description='Сравнить 2 кубика')
async def clash(inter, кубики: str):
    await f.clash(inter, кубики)
# добавить персонажа в память
@bot.slash_command(name='персонаж', description='Задать характеристики персонажа для боя')
async def createChar(inter, имя: str, оз: commands.Range[int, 1, ...], оп: commands.Range[int, 1, ...], стамина: commands.Range[int, 1, ...], знач_иниц: str, резисты: str):
    await b.createChar(inter, имя, оз, оп, стамина, знач_иниц, резисты)
@bot.slash_command(name='бой', description='Команды, связанные с боем')
async def battle(inter):
    pass
# голос за конец боя
@battle.sub_command(name='закончить', description='Закончить текущий бой')
async def endBattle(inter):
    await b.endBattle(inter)
# отменить конец боя
@battle.sub_command(name='продолжить', description='Отменить конец текущего боя')
async def cancelEndBattle(inter):
    await b.cancelEndBattle(inter)
# начать бой
@battle.sub_command(name='начать', description='Начать бой с заданными персонажами')
async def startBattle(inter):
    await b.startBattle(inter)
# добавить перса в бой
@battle.sub_command(name='добавить', description='Добавить персонажа в текущий бой')
async def addChar(inter, персонаж: str, команда: int = commands.Param(choices=[1, 2])):
    await b.addChar(inter, персонаж, команда-1)
# инфо о бое
@battle.sub_command(name='инфо', description='Информация о текущем бое')
async def battleInfo(inter):
    await b.battleInfo(inter)
# дамаг/отхил
@battle.sub_command(name='урон', description='Нанести урон персонажу')
async def damage(inter, персонаж: str, количество: int, тип: str = commands.Param(choices={'Чистый': 'pure','Физический': 'phys', 'Магический': 'mag', 'Потеря ОЗ': 'pure_hp', 'Чистый оглушающий': 'pure_sp'}), уменьшение: int = 0):
    await b.damageChar(inter, персонаж, количество, тип, уменьшение)
@battle.sub_command(name='хил', description='Восстановить ОЗ и/или ОП персонажу')
async def heal(inter, персонаж: str, количество: commands.Range[int, 1, ...], тип: str = commands.Param(choices={'ОЗ': 'hp','ОП': 'sp', 'Общий': 'both'})):
    await b.healChar(inter, персонаж, количество, тип)
# использование скилла
@battle.sub_command(name='использовать', description='Использовать приём за персонажа и добавить ему откат')
async def useStamina(inter, персонаж: str, стоимость: commands.Range[int, 0, ...], приём: str='', откат: commands.Range[int, 0, ...]=0):
    await b.useSkill(inter, персонаж, стоимость, приём, откат)
# добавление/убирание стамины
@battle.sub_command(name='стамина', description='Изменить стамину персонажа')
async def regenStamina(inter, персонаж: str, количество: int):
    await b.changeStamina(inter, персонаж, количество)
# следующий ход
@battle.sub_command(name='ход', descripton='Закончить ход')
async def nextTurn(inter):
    await b.nextTurn(inter)
# наложить эффект
@battle.sub_command(name='эффект', descripton='Наложить эффект на персонажа')
async def addEffect(inter, персонаж: str, эффект: str, количество: commands.Range[int, 1, ...], когда: str = commands.Param(choices={'Сразу': 'this', 'Со следующего хода': 'next'})):
    await b.addEffect(inter, персонаж, эффект, количество, когда)
# поиск приёмов
@bot.slash_command(name='приёмы', description='Поиск приёмов по названию')
async def searchSkills(inter, приём_1: str, приём_2: str = ''):
    await f.searchSkills(inter, [приём_1, приём_2])
# Run!
bot.run(TOKEN)