# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
""" Userbot module for having some fun with people. """

import os
import urllib
import requests
from re import sub
from cowpy import cow
from asyncio import sleep
from collections import deque
from random import choice, getrandbits, randint

from userbot import bot, CMD_HELP
from userbot.events import register
from userbot.modules.admin import get_user_from_event

# ================= CONSTANT =================
GAMBAR_KONTL = """
⣠⡶⠚⠛⠲⢄⡀
⣼⠁ ⠀⠀⠀ ⠳⢤⣄
⢿⠀⢧⡀⠀⠀⠀⠀⠀⢈⡇
⠈⠳⣼⡙⠒⠶⠶⠖⠚⠉⠳⣄
⠀⠀⠈⣇⠀⠀⠀⠀⠀⠀⠀⠈⠳⣄
⠀⠀⠀⠘⣆ ⠀⠀⠀⠀ ⠀⠈⠓⢦⣀
⠀⠀⠀⠀⠈⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠲⢤
⠀⠀⠀⠀⠀⠀⠙⢦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧
⠀⠀⠀⠀⠀⠀⠀⡴⠋⠓⠦⣤⡀⠀⠀⠀⠀⠀⠀⠀⠈⣇
⠀⠀⠀⠀⠀⠀⣸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡄
⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠀⢹⡄⠀⠀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠃
⠀⠀⠀⠀⠀⠀⠀⠙⢦⣀⣳⡀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠏
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⢦⣀⣀⣀⣀⣠⡴⠚⠁⠉⠉⠉
"""

GAMBAR_TENGKORAK = """
░░░░░░░░░░░░░▄▐░░░░
░░░░░░░▄▄▄░░▄██▄░░░
░░░░░░▐▀█▀▌░░░░▀█▄░
░░░░░░▐█▄█▌░░░░░░▀█▄
░░░░░░░▀▄▀░░░▄▄▄▄▄▀▀
░░░░░▄▄▄██▀▀▀▀░░░░░
░░░░█▀▄▄▄█░▀▀░░░░░░
░░░░▌░▄▄▄▐▌▀▀▀░░░░░
░▄░▐░░░▄▄░█░▀▀░░░░░
░▀█▌░░░▄░▀█▀░▀░░░░░
░░░░░░░░▄▄▐▌▄▄░░░░░
░░░░░░░░▀███▀█▄░░░░
░░░░░░░▐▌▀▄▀▄▀▐░░░░
░░░░░░░▐▀░░░░░░▐▌░░
░░░░░░░█░░░░░░░░█░░
░░░░░░▐▌░░░░░░░░░█░
"""

GAMBAR_WANITA = """
´´´´´████████´´
´´`´███▒▒▒▒███´´´´´
´´´███▒●▒▒●▒██´´´
´´´███▒▒👄▒▒██´´
´´█████▒▒████´´´´´
´█████▒▒▒▒███´´
█████▒▒▒▒▒▒███´´´´
´´▓▓▓▓▓▓▓▓▓▓▓▓▓▒´´
´´▒▒▒▒▓▓▓▓▓▓▓▓▓▒´´´´´
´.▒▒▒´´▓▓▓▓▓▓▓▓▒´´´´´
´.▒▒´´´´▓▓▓▓▓▓▓▒
..▒▒.´´´´▓▓▓▓▓▓▓▒
´▒▒▒▒▒▒▒▒▒▒▒▒
´´´´´´´´´███████´´´´
´´´´´´´´████████´´´´´´
´´´´´´´█████████´´´´´
´´´´´´██████████´´´
´´´´´´██████████´´
´´´´´´´█████████´
´´´´´´´█████████´
´´´´´´´´████████´´´
´´´´´´´´´´´▒▒▒▒▒´´´
´´´´´´´´´´▒▒▒▒▒´´´
´´´´´´´´´´▒▒▒▒▒´´´
´´´´´´´´´´▒▒´▒▒´´´
´´´´´´´´´▒▒´´▒▒´´´
´´´´´´´´´´▒▒´´´▒▒´´´
´´´´´´´´´▒▒´´´▒▒´´´
´´´´´´´´▒▒´´´´´▒▒´´´
´´´´´´´´▒▒´´´´´´▒▒´´´
´´´´´´´´███´´´´███´´´
´´´´´´´´████´´███´´´
´´´´´´´´█´´███´´████´´´
"""

GAMBAR_LIKE = """
┈┈┈┈┈┈▕▔╲
┈┈┈┈┈┈┈▏▕
┈┈┈┈┈┈┈▏▕▂▂▂
▂▂▂▂▂▂╱┈▕▂▂▂▏
▉▉▉▉▉┈┈┈▕▂▂▂▏
▉▉▉▉▉┈┈┈▕▂▂▂▏
▔▔▔▔▔▔╲▂▕▂▂▂▏
"""

GAMBAR_IPHONE = """
╭━━━━━━━╮
┃  ● ══   ┃
┃███████┃
┃███████┃
┃███████┃
┃███████┃
┃███████┃
┃███████┃
┃███████┃
┃███████┃
┃     ○    ┃
╰━━━━━━━╯
"""

# =============================================
 
 
@register(outgoing=True, pattern=r"^\.(?:wan|wanita)\s?(.)?")
async def emoji_wanita(e):
    emoji = e.pattern_match.group(1)
    wanita = GAMBAR_WANITA
    if emoji:
        wanita = wanita.replace('😂', emoji)
    await e.edit(wanita)


@register(outgoing=True, pattern=r"^\.(?:iph|iphone)\s?(.)?")
async def emoji_iphone(e):
    emoji = e.pattern_match.group(1)
    iphone = GAMBAR_IPHONE
    if emoji:
        iphone = iphone.replace('😂', emoji)
    await e.edit(iphone)
    
    
     
CMD_HELP.update({
  
 "gambar": "⎙__** NAMA MODUL :** abstrak__"
    "\n\n❏ **CMD      ➜ ** |`.wan` |`.sk` |`.hi` |`.iph` | "
     "\n┗  **USAGE ➜ ** `cek aja tod.`"
})
 
