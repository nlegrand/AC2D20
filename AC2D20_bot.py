#!/usr/bin/env python3

import discord
import re
import random
import sqlite3
import json
from AC2D20 import AC2D20Character

ac2d20 = discord.Client()


@ac2d20.event
async def on_ready():
    print('Coucou, je suis {0.user}'.format(ac2d20))


@ac2d20.event
async def on_message(message):
    if message.author == ac2d20.user:
        return

    if message.content.startswith('Macron'):
        await message.channel.send('Prout Prout Prout !')

    challenge_dice = re.match(r"^\s*([0-9]+)(🐙)\s*$", message.content)
    d20 = re.match(r"^\s*([0-5])d20\s+diff:\s*([0-5])\s+seuil:\s*(1{0,1}[0-9])\s+spé:\s*([0-1])\s*$", message.content)
    cd_possibilities = [1, 2, 0, 0, "🐙", "🐙"]

    if challenge_dice is not None:
        ncd = int(challenge_dice.group(1))
        if ncd < 21:
            damage = 0
            effect = 0
            results = []
            for i in range(ncd):
                res = random.choice(cd_possibilities)
                print(f"résultat : {res}")
                results.append(res)
                if res == 1 or res == 2:
                    damage += res
                elif res == '🐙':
                    effect += 1
                    damage += 1
            await message.channel.send(
                f"`[{','.join([str(x) for x in results])}] => dommages : {damage}, effets: {effect}`"
            )
        else:
            await message.channel.send('`Ça fait beaucoup trop de dés de défi, vous mourrez !`')
    elif d20 is not None:
        dicen = int(d20.group(1))
        diff = int(d20.group(2))
        treshold = int(d20.group(3))
        focus = int(d20.group(4))
        results = []
        successes = 0
        complications = 0
        for i in range(dicen):
            res = random.randrange(1, 21)
            results.append(res)
            if res <= treshold:
                if focus == 1 or res == 1:
                    successes += 2
                else:
                    successes += 1
            if res == 20:
                complications += 1
            elif res >= 19 and diff == 2:
                complications += 1
            elif res >= 18 and diff == 3:
                complications += 1
            elif res >= 17 and diff == 4:
                complications += 1
            elif res >= 16 and diff == 5:
                complications += 1
        await message.channel.send(f"`[{','.join([str(x) for x in results])}] => succès: {successes}, complications: {complications}`")

    show_point = re.match(r"^\s*!(élan|menace)\s*$", message.content)
    if (show_point is not None):
        pointname = show_point.group(1)
        await message.channel.send(fetch_points(pointname))
    op_on_point = re.match(r"^\s*!(élan|menace)\s*([\+\-=])\s*([1-9])\s*$", message.content)
    if (op_on_point is not None):
        pointname = op_on_point.group(1)
        operator = op_on_point.group(2)
        num = int(op_on_point.group(3))
        await message.channel.send(update_points(pointname, operator, num))

    show_char = re.match(r"^\s*!perso\s*(asha|jean|émile|renato)\s*$", message.content)
    if (show_char is not None):
        perso = show_char.group(1)
        await message.channel.send(print_character(perso))

    show_char_detail = re.match(r"^\s*!perso\s*(asha|jean|émile|renato)\s*(caracs|santé|armes)\s*$", message.content)
    if (show_char_detail is not None):
        perso = show_char_detail.group(1)
        character = AC2D20Character(perso)
        detail = show_char_detail.group(2)
        if detail == "caracs":
            res = print_attributes(character, 2) + "\n"
            res += print_skills(character, 2)
            await message.channel.send(f"```#Caracs de {perso} :\n\n{res}```")
        elif detail == 'santé':
            res = f"Stress :\n{print_dict(character.stats('stress'), 2)}"
            res += f"Blessures :\n{print_dict(character.stats('blessures'), 2)}"
            await message.channel.send(f"```#Santé de {perso} :\n\n{res}```")
        elif detail == 'armes':
            res = f"Armes :\n{print_dict(character.stats('armes'), 2)}"
            await message.channel.send(f"```#Armes de {perso} :\n\n{res}```")
    show_context = re.match(r"^\s*!context\s*$", message.content)

    if (show_context is not None):
        con = sqlite3.connect('ac2d20.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select Fichier from aventure where Courante = 1")
        r = cur.fetchone()
        con.close()
        await message.channel.send(f"https://github.com/nlegrand/AC2D20/blob/main/{r['Fichier']}")

    show_help = re.match(r"^\s*!aide\s*$", message.content)
    if (show_help is not None):
        res = "Commandes de AC2D20 :\n"
        res += "  [0-9]🐙 : envoie n dés de défi\n"
        res += "  [0-5]d20 diff:[0-5] seuil:[0-1][0-9] spé:[0-1]\n"
        res += "    le jet de d20, exemple avec 2 dés, une diff de 2,\n"
        res += "    attributs + compétences à 12 et pas de spécialité :\n"
        res += "    2d20 diff:2 seuil:12 spé:0\n"
        res += "  !(élan|menace) : montre la réserve d’élan ou de menace\n"
        res += "  !(élan|menace) (+|-)[0-9]: ajoute ou enlève des points de menace ou d’élan\n"
        res += "  !context : lien vers le contexte de l’histoire\n"
        res += "  !perso <perso> : description du perso\n"
        res += "  !perso <perso> caracs : les caracs du perso\n"
        res += "  !perso <perso> santé : l’état de santé du perso\n"
        res += "  !perso <perso> armes : les armes du perso\n"
        res += "  !(stress|fatigue) <perso> [0-9] : positionne le stress ou la fatigue\n"
        res += "  !blessure <perso> <bla bla bla> : ajoute une blessure\n"
        res += "  !blessure <perso> <remove> : retire toutes les blessures\n"
        res += "  !fortune <perso> [0-3] : positionne les points de fortune\n"
        res += "  <perso> peut être une de ces quatre valeurs : "
        res += "asha, émile, jean, renato\n"

        await message.channel.send(f"```{res}```")

    set_stress = re.match(r"^\s*!(stress|fatigue)\s*(asha|jean|émile|renato)\s*(1{0,1}[0-9])\s*$", message.content)
    if set_stress is not None:
        stress_type = set_stress.group(1)
        if stress_type == "stress":
            stress_type = "perdus"
        perso = set_stress.group(2)
        value = int(set_stress.group(3))
        character = AC2D20Character(perso)
        character.stress(stress_type, value)
        res = f"Stress :\n{print_dict(character.stats('stress'), 2)}"
        res += f"Blessures :\n{print_dict(character.stats('blessures'), 2)}"
        await message.channel.send(f"```#Santé de {perso} :\n\n{res}```")

    set_injury = re.match(r"^\s*!blessure\s+(asha|jean|émile|renato)\s+(.{3,512})$", message.content)
    if set_injury is not None:
        perso = set_injury.group(1)
        argstr = set_injury.group(2)
        character = AC2D20Character(perso)
        character.injury(arg=argstr)
        res = f"Stress :\n{print_dict(character.stats('stress'), 2)}"
        res += f"Blessures :\n{print_dict(character.stats('blessures'), 2)}"
        await message.channel.send(f"```#Santé de {perso} :\n\n{res}```")

    set_fortune = re.match(r"^\s*!fortune\s+(asha|jean|émile|renato)\s+([1-3])\s*$", message.content)
    if set_fortune is not None:
        perso = set_fortune.group(1)
        argstr = set_fortune.group(2)
        character = AC2D20Character(perso)
        res = character.fortune(int(argstr))
        await message.channel.send(f"```#Fortune de {perso} : {res}```")



def print_character(character_name):
    character = AC2D20Character(character_name)
    sheet = '```'
    sheet += f"Nom : {character.stats('nom')}\n"
    sheet += f"Nationalité : {character.stats('nationalité')}\n"
    sheet += f"Archétype : {character.stats('archétype')}\n"
    sheet += f"Antécédents : {character.stats('antécédents')}\n"
    sheet += f"Caractéristique : {character.stats('caractéristique')}\n"
    sheet += f"Vérités :\n{print_tab(character.stats('vérités'), 2)}"
    sheet += f"Langues :\n{print_tab(character.stats('languages'), 2)}"
    sheet += "\n"
    sheet += f"Courage : {character.stats('courage')}\n"
    sheet += f"Armure : {character.stats('armure')}\n"
    sheet += f"Fortune : {character.stats('fortune')}\n"
    sheet += "\n"
    sheet += f"Talents :\n{print_dict(character.stats('talents'), 2)}"
    sheet += '```'
    return sheet


def print_value(character_name, key):
    character = AC2D20Character(character_name)
    res = ''
    if isinstance(character.stats(key), dict):
        res = print_dict(character.stats(key), 2)
    elif isinstance(character.stats(key), list):
        res = print_tab(character.stat(key), 2)
    else:
        res += f"key : {character.stat(key)}\n"
    return res


def print_attributes(character, indent):
    res = 'Attributs :\n\n'
    for k, v in character.allstats['attributs'].items():
        res += f"{' ' * indent}- {k} : {v}"
        if v == 9:
            res += " (+1 )"
        elif v == 10 or v == 11:
            res += " (+2)"
        elif v == 12 or v == 13:
            res += " (+3)"
        elif v == 14 or v == 15:
            res += " (+4)"
        elif v >= 16:
            res += " (+5)"
        res += "\n"        
    return res


def print_skills(character, indent):
    res = 'Compétences :\n\n'
    for k, v in character.allstats['compétences'].items():
        res += f"{' ' * indent}- {k} : {v['score']}"
        if "spécialité" in v:
            res += f"({', '.join(v['spécialité'])})"
        res += "\n"
    return res

def print_tab(tab, indent):
    res = ''
    for v in tab:
        if isinstance(v, dict):
            res = print_dict(v, indent + 2)
        else:
            res += f"{' ' * indent}- {v}\n"
    return res


def print_dict(value, indent):
    res = ''
    for k, v in value.items():
        if isinstance(v, list):
            res += f"{' ' * indent}- {k} :\n{print_tab(v, indent + 2)}"
        elif isinstance(v, dict):
            res += f"{' ' * indent}- {k} :\n{print_dict(v, indent + 2)}"
        else:
            res += f"{' ' * indent}- {k} : {v}\n"
    return res


def fetch_points(pointname):
    name = ''
    if pointname == 'élan':
        name = 'Élan'
    elif pointname == 'menace':
        name = 'Menace'
    con = sqlite3.connect('ac2d20.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from points where Nom=:name", {'name': name})
    r = cur.fetchone()
    con.close()
    return r['Valeur']


def update_points(pointname, operator, num):
    name = ''
    if pointname == 'élan':
        name = 'Élan'
    elif pointname == 'menace':
        name = 'Menace'
    current_points = fetch_points(pointname)
    new_points = 0
    if operator == '+':
        new_points = current_points + num
    elif operator == '-':
        new_points = current_points - num
    elif operator == '=':
        new_points = num
    if new_points < 0:
        new_points = 0
    elif new_points > 6 and name == 'Élan':
        new_points = 6
    con = sqlite3.connect('ac2d20.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("UPDATE points set Valeur =:new where Nom=:name", {"new": new_points, "name": name})
    con.commit()
    cur.execute("select * from points where Nom=:name", {'name': name})
    r = cur.fetchone()
    con.close()
    return r['Valeur']


fh = open('config.json', 'r')
config = json.load(fh)
ac2d20.run(config['token'])
