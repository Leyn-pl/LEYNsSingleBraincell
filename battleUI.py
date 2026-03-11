import random
from features import log
import disnake as ds
import strings as ss
from battles import *

# global
currentBattle: Battle|None = None
storedChars: list[Character] = []
battleStarted = False

endingBattle = set()

def loadTestChars():
    global storedChars
    for char in TestChars:
        storedChars.append(char)
    log('Загружены тестовые персонажи', 'battleUI')

def setvar(var, value):
    globals()[var] = value

def getCharByName(name) -> Character|None:
    try:
        char = storedChars[list(map(lambda x: x.name, storedChars)).index(name)]
    except ValueError:
        return None
    return char

def battleSummary(battle: Battle) -> tuple[ds.Embed, ds.Embed]:
    team1 = ds.Embed(
        title='Команда 1',
        color=ss.color
    )
    for char in battle.teams[0]:
        team1.add_field(
            name=char.name,
            value=char.info(),
            inline=True
        )
    if len(battle.teams[0]) > 0:
        team1.add_field(name='Порядок ходов:', value=' -> '.join(battle.getTurnOrder(0)), inline=False)
    else:
        team1.add_field(name='Пусто', value='', inline=False)
    team2 = ds.Embed(
        title='Команда 2',
        color=ss.color
    )
    for char in battle.teams[1]:
        team2.add_field(
            name=char.name,
            value=char.info(),
            inline=True
        )
    if len(battle.teams[1]) > 0:
        team2.add_field(name='Порядок ходов:', value=' -> '.join(battle.getTurnOrder(1)), inline=False)
    else:
        team2.add_field(name='Пусто', value='', inline=False)
    return team1, team2

async def debug(inter: ds.ApplicationCommandInteraction, cmd: str):
    global skillsLoaded, currentBattle, storedChars, battleStarted, endingBattle
    if inter.author.id != ss.devid:
        await inter.response.send_message('Эта команда доступна только моему создателю.', ephemeral=True)
        return
    try:
        exec(f'log({cmd}, "debug")')
    except Exception:
        try:
            exec(cmd)
            log('Команда выполнена в в режиме строки.', 'debug')
        except Exception as e:
            log(str(e), 'debug.error')
    await inter.response.send_message(f'Выполнен код:\n```{cmd}```', ephemeral=True)

async def createChar(inter: ds.ApplicationCommandInteraction, name, hp, sp, stam, init_dice, resists):
    try:
        char = Character(name, hp, sp, stam, resists.split(' '))
    except ValueError:
        await inter.response.send_message(ss.invalidResistFormat, ephemeral=True)
        return
    if name in [i.name for i in storedChars]:
        await inter.response.send_message(ss.nameTaken + f'{name}-1, {name}-2, ...', ephemeral=True)
        return
    try:
        for value in init_dice.split(' '):
            char.addDice(int(value))
    except ValueError:
        await inter.response.send_message(ss.invalidInitFormat, ephemeral=True)
        return
    storedChars.append(char)
    await inter.response.send_message(f'(персонаж добавлен в память)\n-# // {char}')
    log(f'Персонаж создан: {char} <<< {inter.author.name}', 'battleUI')

async def endBattle(inter: ds.ApplicationCommandInteraction):
    global endingBattle, currentBattle, battleStarted
    if currentBattle is None:
        await inter.response.send_message(ss.noBattle, ephemeral=True)
        return
    endingBattle.add(inter.author.id)
    if len(endingBattle) < 2:
        await inter.response.send_message(ss.confirmEndBattle)
        return
    currentBattle = None
    battleStarted = False
    await inter.response.send_message(ss.battleOver)
    log(f'Бой закончен <<< {endingBattle}', 'battleUI')
    endingBattle.clear()

async def cancelEndBattle(inter: ds.ApplicationCommandInteraction):
    global endingBattle
    if not inter.author.id in endingBattle:
        await inter.response.send_message(ss.youDidntVote, ephemeral=True)
        return
    endingBattle.remove(inter.author.id)
    await inter.response.send_message(ss.cancelEndBattle)

async def addChar(inter: ds.ApplicationCommandInteraction, char: str, team: int):
    global currentBattle
    if currentBattle is None:
        currentBattle = Battle()
        log(f'Новый бой начат <<< {inter.author.id}', 'battleUI')
    char = getCharByName(char)
    if char is None:
        await inter.response.send_message(ss.charNotFound + '\n'.join([i.name for i in storedChars]),ephemeral=True)
        return
    if currentBattle.addChar(char, team):
        await inter.response.send_message(ss.nameTaken, ephemeral=True)
        return
    in_battle = ', '.join([i.name for i in currentBattle.chars])
    await inter.response.send_message(f'({char.name} добавлен в бой за команду {team+1})\n-# // Сейчас в бою: {in_battle}')
    log(f'Персонаж "{char}" добавлен в бой за команду {team+1} <<< {inter.author.id}', 'battleUI')

async def battleInfo(inter: ds.ApplicationCommandInteraction):
    if currentBattle is None:
        await inter.response.send_message(ss.noBattle, ephemeral=True)
        return
    team1, team2 = battleSummary(currentBattle)
    response = f'(ход {currentBattle.turn})' if currentBattle.turn > 0 else ''
    await inter.response.send_message(response, embeds=[team1, team2])

async def damageChar(inter: ds.ApplicationCommandInteraction, char: str, amount: int, dmgtype: str, dmg_reduction: int):
    if currentBattle is None:
        await inter.response.send_message(ss.noBattle, ephemeral=True)
        return
    char = getCharByName(char)
    if char is None:
        await inter.response.send_message(ss.charNotFound + '\n'.join([i.name for i in currentBattle.chars]), ephemeral=True)
        return
    hp_lost, sp_lost, stunned, dead = char.damage(amount, dmgtype, dmg_reduction)
    dmgtype = ss.damageTypes[dmgtype]
    if battleStarted and amount > 0:
        response = f'**{char.name} теряет {hp_lost} ОЗ и {sp_lost} ОП'
        if dead:
            response += ' и умирает.**'
        elif stunned:
            response += ' и оглушается.**'
        else:
            response += '.**'
    else:
        response = f'({char.name} нанесено {amount} {dmgtype} урона)'
    await inter.response.send_message(response)
    log(f'Нанесено {amount} {dmgtype} урона "{char}" <<< {inter.author.name}', 'battleUI')

async def healChar(inter: ds.ApplicationCommandInteraction, char: str, amount: int, healtype: str):
    if currentBattle is None:
        await inter.response.send_message(ss.noBattle, ephemeral=True)
        return
    char = getCharByName(char)
    if char is None:
        await inter.response.send_message(ss.charNotFound + '\n'.join([i.name for i in currentBattle.chars]), ephemeral=True)
        return
    char.heal(amount, healtype)
    healtype = ss.healTypes[healtype]
    if battleStarted:
        response = f'**{char.name} восстанавливает {amount} {healtype}.**'
    else:
        response = f'({char.name} восстановлено {amount} {healtype})'
    await inter.response.send_message(response)
    log(f'Восстановлено {amount} {healtype} "{char}" <<< {inter.author.name}', 'battleUI')

async def useSkill(inter: ds.ApplicationCommandInteraction, char: str, cost: int, skill: str, cooldown: int):
    if currentBattle is None:
        await inter.response.send_message(ss.noBattle, ephemeral=True)
        return
    char = getCharByName(char)
    if char is None:
        await inter.response.send_message(ss.charNotFound + '\n'.join([i.name for i in currentBattle.chars]), ephemeral=True)
        return
    if char.useStamina(cost):
        await inter.response.send_message(ss.noStamina, ephemeral=True)
        return
    response = f'{char.name} тратит {cost} стамины'
    if skill != '':
        response += f' на приём {skill}'
        if cooldown > 0:
            char.addCooldown(skill, cooldown)
            response += f', он теперь в перезарядке {cooldown} ходов'
    await inter.response.send_message(f'({response})')
    log(f'"{char}" -{cost} стамины на "{skill}" с кд {cooldown}', 'battleUI')

async def changeStamina(inter: ds.ApplicationCommandInteraction, char: str, amount: int):
    if currentBattle is None:
        await inter.response.send_message(ss.noBattle, ephemeral=True)
        return
    char = getCharByName(char)
    if char is None:
        await inter.response.send_message(ss.charNotFound + '\n'.join([i.name for i in currentBattle.chars]), ephemeral=True)
        return
    if amount == 0:
        await inter.response.send_message('Ничего не изменилось.', eephemeral=True)
        return
    elif amount > 0:
        amount = char.regenStamina(amount)
        await inter.response.send_message(f'({char.name} восстанавлено {amount} стамины)')
        log(f'Восстановлено {amount} стамины "{char}" <<< {inter.author.name}', 'battleUI')
    else:
        amount = abs(amount)
        if char.useStamina(amount):
            await inter.response.send_message(ss.noStamina, ephemeral=True)
            return
        await inter.response.send_message(f'({char.name} убрано {amount} стамины)')
        log(f'Убрано {amount} стамины "{char}" <<< {inter.author.name}', 'battleUI')

async def addEffect(inter: ds.ApplicationCommandInteraction, char: str, effect: str, value: int, when: str):
    if currentBattle is None:
        await inter.response.send_message(ss.noBattle, ephemeral=True)
        return
    char = getCharByName(char)
    if char is None:
        await inter.response.send_message(ss.charNotFound, ephemeral=True)
        return
    next_turn = True if when == 'next' else False
    char.effect(effect, value, next_turn)
    response = f'{char.name} получает {value}x {effect}' if not next_turn else f'{char.name} получит {value}x {effect} в следующем ходу'
    await inter.response.send_message(f'({response})')
    tolog = f'Наложено {value}x {effect} на {char}' if not next_turn else f'В следующем ходу будет наложено {value}x {effect} на {char}'
    log(f'{tolog} <<< {inter.author.name}', 'battleUI')

async def startBattle(inter: ds.ApplicationCommandInteraction):
    global battleStarted
    if currentBattle is None or len(currentBattle.teams[0]) * len(currentBattle.teams[1]) == 0:
        await inter.response.send_message(ss.teamsNotFull, ephemeral=True)
        return
    battleStarted = True
    currentBattle.turn += 1
    team1, team2 = battleSummary(currentBattle)
    await inter.response.send_message('**Бой начинается. Ход 1, Фаза I.**', embeds=[team1, team2])

async def nextTurn(inter: ds.ApplicationCommandInteraction):
    if not battleStarted:
        await inter.response.send_message(ss.noBattle, ephemeral=True)
        return
    old_phase = currentBattle.getPhase()
    currentBattle.turn += 1
    effects_over = {}
    for char in currentBattle.chars:
        char_effects_over = char.nextTurn(currentBattle.getPhase())
        if len(char_effects_over):
            effects_over.update({char.name: char_effects_over})
    response = f'**Ход {currentBattle.turn}'
    if currentBattle.getPhase() != old_phase:
        response += f' Начинается фаза {ss.romans[currentBattle.getPhase()]}.**'
        for char in currentBattle.chars:
            char.nextPhase()
            if currentBattle.getPhase() == 3:
                char.addDice(random.choice(char.dice))
    else:
        response += '.**'
    if effects_over:
        for name in effects_over.keys():
            eflist = ', '.join(effects_over[name])
            response += f'\n({name} теряет {eflist})'
    team1, team2 = battleSummary(currentBattle)
    await inter.response.send_message(f'{response}', embeds=[team1, team2])