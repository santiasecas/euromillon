#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import configparser
import logging
import mechanize

from bs4 import BeautifulSoup as bs

from telegram import ForceReply, Update
from telegram.ext import Updater, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


config = configparser.ConfigParser()
config.read('config.ini')

ADMIN    = config['BOT_CONFIG']['ADMIN']
USUARIO  = config['BOT_CONFIG']['USUARIO']
PASSWORD = config['BOT_CONFIG']['PASSWORD']

URL   = "https://juegos.loteriasyapuestas.es/acceder/login"
URL_2 = 'https://juegos.loteriasyapuestas.es:443/jugar/cas/apuestas/historicos'

solicitud = False

def start(update, context):
    nuevoUsuario = str(update.message.from_user.username)
    context.bot.send_message(ADMIN,'Nuevo usuario: @' + nuevoUsuario)
    #update.message.reply_text('Welcome ' + nuevoUsuario + '\nYou can contact me at @santiasecas')

def limpiar_texto(texto):
    return ' '.join(texto.strip().replace('\n','').replace('\t','').split())

def recupera_info_euromillon():
    global solicitud
    res = ''
    try:
        br = mechanize.Browser()
        br.open(URL)
        br.select_form(nr=0)
        br.form['username'] = USUARIO
        br.form['password'] = PASSWORD
        br.submit()

        pagina = br.open(URL_2).read()
        sopa = bs(pagina, features="html5lib")

        res  = 'Saldo actual: '
           
        cantidad = sopa.find("span",{"titulo-valor"})
        res += limpiar_texto(cantidad.text) + '\n\n'

        res += 'Últimas 5 apuestas:\n'

        apuestas = sopa.findAll("li",{"decripcion oculta_mobile last"})
        cont = 1

        for apuesta in apuestas:
            res += f'Apuesta {str(cont)}:\n'
            res += limpiar_texto(apuesta.text) + '\n'
            cont += 1
    except:
        res = 'Ha fallado la recuperación de información'
    finally:
        solicitud = False
    return res

def obtener_informacion_euromillon(update, context):
    global solicitud
    if solicitud == False:
        update.message.reply_text('Se está consultando la información... Espera un momento.')
        res = recupera_info_euromillon()
        update.message.reply_text(res)
    elif solicitud == True:
        update.message.reply_text('Ya has hecho una consulta. Espera la respuesta')

def main():
    TOKEN = config['BOT_CONFIG']['BOTTOKEN']
    PORT = 443
    SERVER = config['BOT_CONFIG']['SERVER']
    
    
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('saldo', obtener_informacion_euromillon))
        
    updater.start_polling()
    
    updater.idle()
    

if __name__ == '__main__':
    main()