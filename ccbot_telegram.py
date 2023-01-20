import telebot # Para utilizar la API de Telegram
import pyowm # Para utilizar la API del OpenWeather

from config import * # Importo key y token
from telebot.types import ReplyKeyboardMarkup # Para crear botones
from telebot.types import ForceReply # Para citar un mensaje
from pyowm.utils.config import get_default_config # Para cambiar el lenguaje

# Esto solo afecta detailed_status, cambio el lenguaje a español
config_dict = get_default_config()
config_dict['language'] = 'es'


# Se instancia el bot con el token
bot = telebot.TeleBot(TOKEN)
# Se instancia el objeto global de OWM
owm = pyowm.OWM(API_KEY)
# Se instancia diccionario para guardar la variable de ciudad y pais
lugar = {}
# Se instancia variable global para el contador
contador = 0

# Que responda a los comandos: /start y /help
@bot.message_handler(commands=["start","help"])

def iniciar_chat(message):
    # Se instancian las opciones     
    markup = ReplyKeyboardMarkup(one_time_keyboard=True).add("¡Quiero saber el clima!").add("¡Quiero contar!")
    # Da la bienvenida y muestra los botones
    bot.reply_to(message,"¡Hola! ¿Qué necesitas?", reply_markup = markup)
    contar_mensaje(1)

# Función del contador
def contar_mensaje(num):
    global contador
    contador += num
    
# Responde a los mensajes de texto que no son comandos y responde a las opciones a elegir
@bot.message_handler(content_types=["text"])

def opciones_mensaje(message):
    if message.text and message.text.startswith("/"):
        bot.send_message(message.chat.id, "Comando no disponible")
        contar_mensaje(1)
    elif message.text == "¡Quiero saber el clima!":
        contar_mensaje(1)
        preguntar_ciudad(message)
    elif message.text == "¡Quiero contar!":
        contar_mensaje(1)
        opcion_contador(message)
    # Si es otro tipo de mensaje, que no es opción ni comando inexistente, vuelve a iniciar el chat
    else:
        iniciar_chat(message)
        
# Se elige la opción del clima
@bot.message_handler(content_types=["text"])

def preguntar_ciudad(message):
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "¿De qué ciudad?", reply_markup = markup)
    bot.register_next_step_handler(msg, preguntar_pais)
    
def preguntar_pais(message):
    # Se almacena el dato de message.text en la variable "ciudad" del diccionario, para que no se sobreescriba en el próximo message.text
    lugar[message.chat.id] = {}
    lugar[message.chat.id]["ciudad"] = message.text
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "¿De qué país? Escriba el código, ej: UY", reply_markup = markup)
    bot.register_next_step_handler(msg, opcion_clima)
    
def opcion_clima(message):
    # Se repite lo mismo pero con pais
    lugar[message.chat.id]["país"] = message.text.upper()
    # Se instancia el weather_manager() para consultar los datos meterológicos
    mgr = owm.weather_manager()
    # Si la ciudad y el pais son correctos, el bot envía la información: estado, temperatura, humedad y viento. En caso de
    # no ser correcto, lanza una excepción.
    try:
        obs = mgr.weather_at_place(lugar[message.chat.id]["ciudad"] + ',' + lugar[message.chat.id]["país"])
        w = obs.weather
        wind = w.wind().get('speed',0)*3,6 #Devuelve una tupla

        clima = f"Estado: {w.detailed_status.capitalize()}\n"
        clima += f"Temperatura: {w.temperature(unit='celsius')['temp']} °C\n"
        clima += f"Humedad: {w.humidity}%\n"
        clima += f"Viento: {abs(sum(wind))} km" #Vuelvo la tupla un int para redondear el valor

        bot.send_message(message.chat.id, clima)
    except:
        bot.send_message(message.chat.id, "Error: Uno o más datos parecen ser incorrectos")
    contar_mensaje(2)


# Se elige la opción de contar
def opcion_contador(message):
    bot.send_message(message.chat.id, f"Has enviado un total de {contador} mensajes")

# MAIN -----------------------------------------
if __name__ == "__main__":
    # Comprobar que se inició
    print("Iniciando bot")
    # Bucle infinito en donde comprueba si hay nuevos mensajes
    bot.infinity_polling()

    
