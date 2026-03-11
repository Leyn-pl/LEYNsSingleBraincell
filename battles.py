class Character:
    def __init__(self, name: str, hp: int, sp: int, stam: int, resists: list, dice: list = []):
        if dice is None:
            dice = []
        for i in range(len(resists)):
            if type(resists[i]) == str: resists[i].replace('x', '').replace('х', '') # англ и рус 'x'
            resists[i] = float(resists[i])
        self.name = name
        self.hp, self.maxhp = hp, hp
        self.sp, self.maxsp = sp, sp
        self.stam, self.maxstam = stam, stam
        self.res_phys = [resists[0], resists[1]]
        self.res_mag = [resists[2], resists[3]]
        self.dice = []
        self.stunned = False
        self.stunEnding = False
        self.dead = False
        self.cooldowns = {}
        self.effects = {}
        self.nextEffects = {}
        for i in dice:
            self.addDice(i)

    def addDice(self, value: int):
        self.dice.append(value)
        self.dice.sort(reverse=True)

    def damage(self, amount: int, dmgtype='pure', reduction=0) -> tuple:
        """Учитывает резисты. Возвращает (hp_lost, sp_lost, stunned, dead)"""
        if self.stunned and dmgtype != 'pure':
            hp_lost, sp_lost = amount*2, 0
        elif dmgtype == 'phys':
            hp_lost = int(amount * self.res_phys[0])
            sp_lost = int(amount * self.res_phys[1])
        elif dmgtype == 'mag':
            hp_lost = int(amount * self.res_mag[0])
            sp_lost = int(amount * self.res_mag[1])
        elif dmgtype == 'pure':
            hp_lost, sp_lost = amount, amount
        elif dmgtype == 'pure_hp':
            hp_lost, sp_lost = amount, 0
        elif dmgtype == 'pure_sp':
            hp_lost, sp_lost = 0, amount
        else:
            return 0, 0, self.stunned, self.dead
        if hp_lost > 0: hp_lost -= reduction
        if hp_lost < 0: hp_lost += reduction
        if sp_lost > 0: sp_lost -= reduction
        if sp_lost < 0: sp_lost += reduction
        self.hp = max(self.hp - hp_lost, 0)
        self.sp = max(self.sp - sp_lost, 0)
        self.stunned = self.sp == 0
        self.dead = self.hp == 0
        return hp_lost, sp_lost, self.stunned, self.dead

    def heal(self, amount: int, healtype='hp'):
        if healtype != 'sp': # Хп хил или общий
            self.hp = min(self.hp + amount, self.maxhp)
        if healtype != 'hp': # Сп хил или общий
            self.sp = min(self.sp + amount, self.maxsp)

    def useStamina(self, amount: int) -> bool:
        """Возвращает True, если требуемая стамина меньше текущей (не сработало)"""
        self.stam -= amount
        if self.stam < 0:
            self.stam += amount
            return True
        return False

    def regenStamina(self, amount: int) -> int:
        """Возвращает сколько стамины было восстановлено"""
        before = self.stam
        self.stam = min(self.stam + amount, self.maxstam)
        return self.stam - before

    def addCooldown(self, skill: str, turns: int):
        self.cooldowns.update({skill: turns})

    def removeCooldown(self, skill: str):
        del self.cooldowns[skill]

    def effect(self, effect: str, value: int, next_turn: bool):
        if next_turn:
            if effect in self.nextEffects.keys():
                self.nextEffects[effect] += value
                return
            self.nextEffects.update({effect: value})
        else:
            if effect in self.effects.keys():
                self.effects[effect] += value
                return
            self.effects.update({effect: value})

    def nextTurn(self, phase: int) -> list[str]:
        """Возвращает список закончившихся эффектов"""
        cooldowns_to_remove = []
        # Уменьшение КД
        for spell in self.cooldowns.keys():
            self.cooldowns[spell] -= 1
            if self.cooldowns[spell] == 0:
                cooldowns_to_remove.append(spell)
        for spell in cooldowns_to_remove:
            self.removeCooldown(spell)
        # Выход из стана
        if self.stunned:
            if self.stunEnding:
                self.stunned = False
                self.stunEnding = False
                self.sp = self.maxsp
            else:
                self.stunEnding = True
        else:
            self.regenStamina(phase)
        # Сброс эффектов
        effects_lost = []
        for effect in self.effects.keys():
            effects_lost.append(f'{self.effects[effect]}x {effect}')
        self.effects = self.nextEffects.copy()
        self.nextEffects.clear()
        return effects_lost

    def nextPhase(self):
        self.stam += 2
        self.maxstam += 2

    def __str__(self):
        dice_encoded = ' '.join(map(str, self.dice))
        return f'{self.name} - ОЗ: {self.hp}/{self.maxhp} ОП: {self.sp}/{self.maxsp} Стамина: {self.stam}/{self.maxstam} Иниц: [{dice_encoded}] Физ.Рез: x{self.res_phys[0]}/x{self.res_phys[1]} Маг.Рез: x{self.res_mag[0]}/x{self.res_mag[1]}'

    def info(self):
        out = []
        out.append(f'ОЗ: `{self.hp}`/`{self.maxhp}`')
        out.append( f'ОП: `{self.sp}`/`{self.maxsp}`')
        out.append('⦿'*self.stam + '◯'*(self.maxstam - self.stam))
        init = ' '.join([f'__`[{i}]`__' for i in self.dice])
        out.append(f'Иниц. {init}')
        out.append(f'Защ. *⚔* `x{self.res_phys[0]}`/`x{self.res_phys[1]}`')
        out.append(f'Защ. *✦* `x{self.res_mag[0]}`/`x{self.res_mag[1]}`')
        if self.dead:
            out.append('___МЁРТВ___')
        elif self.stunned:
            out.append('___ОГЛУШЁН___')
        elif len(self.cooldowns) != 0:
            out.append('Откаты:')
            for skill in self.cooldowns.keys():
                out.append(f'`{self.cooldowns[skill]}` - *{skill}*')
        if self.effects:
            out.append('Эффекты:')
            for effect in self.effects.keys():
                out.append(f'`{self.effects[effect]}` - *{effect}*')
        return '\n'.join(out)

class Battle:
    def __init__(self):
        self.chars: list[Character] = []
        self.turn = 0
        self.teams: list[list[Character]] = [[], []]

    def getPhase(self) -> int:
        return (self.turn - 1) // 3 + 1

    def addChar(self, char: Character, team: int) -> bool:
        """Возвращает True, если персонаж уже существует"""
        if char in self.chars:
            return True
        self.chars.append(char)
        self.teams[team].append(char)
        return False

    def getCharTurnOrder(self, team: int) -> list[Character]:
        results = []
        for char in self.teams[team]:
            for value in char.dice:
                results.append([char, value])
        results.sort(key=lambda x: x[1], reverse=True)
        return [result[0] for result in results]

    def getTurnOrder(self, team: int) -> list[str]:
        order = self.getCharTurnOrder(team)
        out = []
        counter = {}
        for char in order:
            counter.update({char: 0})
        for char in order:
            counter[char] += 1
            f = '~~' if char.stunned or char.dead else ''
            dice = '' if len(char.dice) == 1 else f' ({counter[char]})'
            out.append(f'{f}{char.name}{dice}{f}')
        return out

# Тестовые персонажи, загружаются через loadTestChars()
TestChars = [
    Character('М1', 30, 15, 3, [1, 1, 1, 1], [2]),
    Character('М2', 45, 25, 4, [1, 1, 0.5, 0.5], [1, 5]),
    Character('М3', 200, 100, 5, [0.25, 0.25, 0.5, 0.5], [6, 6, 6]),
    Character('О', 50, 25, 3, [0.5, 1.5, 0.5, 1.5], [1, 3]),
    Character('М', 50, 25, 3, [1.5, 0.25, 1.5, 0.25], [1,3]),
    Character('К', 50, 25, 5, [1.5, 1.5, 0.5, 0.5], [4, 3])
]
TestChars[3].damage(20, 'phys')
TestChars[4].damage(35, 'phys')
TestChars[5].useStamina(3)
TestChars[5].addCooldown('Сильное заклинание', 3)