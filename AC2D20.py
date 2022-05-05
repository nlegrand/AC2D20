#!/usr/bin/env python3

import discord
import re
import random
import sqlite3
import json
from tabulate import tabulate

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
    d20 = re.match(r"^\s*([0-5])d20\s+diff:\s*([0-5])\s+seuil:\s*(1{0,1}[0-9])\s+spé:([0-1])\s*$", message.content)
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

    show_char = re.match(r"^\s*!perso\s*([a-z])+\s*$", message.content)
    if (show_char is not None):
        perso = show_char.group(1)
        await message.channel.send(f'''```# Caractéristiques

{print_attributes(perso)}```''')
        await message.channel.send(f'''```#Compétences

{print_skills(perso)}```''')


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


def print_attributes(id):
    con = sqlite3.connect('ac2d20.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from caractéristiques where Personnage = 'asha';")
    con.commit
    r = cur.fetchone()
    con.close()
    headers = r.keys()
    headers.pop(0)
    tab = []
    for k in headers:
        tab.append([k, r[k]])
    return tabulate(tab, [])


def print_skills(id):
    con = sqlite3.connect('ac2d20.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    skills = []
    for r in cur.execute("select * from compétences where Personnage = 'asha';"):
        skills.append([r[1], r[2]])
    con.close()
    return tabulate(skills, [])
    

fh = open('config.json', 'r')
config = json.load(fh)
ac2d20.run(config['token'])
