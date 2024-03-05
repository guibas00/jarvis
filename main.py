import json
import pygame
import tempfile
import requests
import speech_recognition as sr
import pyttsx3

def listar_microfones_disponiveis():
    recognizer = sr.Recognizer()
    microfones = sr.Microphone.list_microphone_names()

    for i, microfone in enumerate(microfones):
        print(f"Índice {i}: {microfone}")

def selecionar_microfone(indice):
    return sr.Microphone(device_index=indice)

def ouvir(microfone):
    recognizer = sr.Recognizer()
    with microfone as source:
        print("Diga algo...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        texto = recognizer.recognize_google(audio, language="pt-BR")
        return texto
    except sr.UnknownValueError:
        print("Não foi possível entender o áudio")
        return None
    except sr.RequestError as e:
        print(f"Erro no serviço de reconhecimento de fala: {e}")
        return None



def texto_para_audio(texto, nome_arquivo_saida="saida_audio.wav"):
    """
    Converte texto em áudio e salva como arquivo WAV.

    Parâmetros:
        texto (str): O texto a ser convertido em áudio.
        nome_arquivo_saida (str): O nome do arquivo de áudio de saída (padrão: "saida_audio.wav").

    Retorna:
        str: O caminho completo do arquivo de áudio de saída.
    """
    # Inicializa o motor de síntese de fala
    engine = pyttsx3.init()

    # Define a propriedade de velocidade de fala (opcional)
    engine.setProperty('rate', 150)  # Ajuste conforme necessário4

    # Salva o áudio em um arquivo WAV
    caminho_arquivo_saida = nome_arquivo_saida
    engine.save_to_file(traduzir_texto_portugues(texto), caminho_arquivo_saida+".wav")

    # Executa o motor de síntese de fala
    engine.runAndWait()

    return caminho_arquivo_saida

def reproduzir_audio(filename):
    # Inicializa o pygame
    pygame.init()

    # Carrega e reproduz o áudio
    pygame.mixer.init()
    pygame.mixer.music.load("./audio_saida.wav")
    pygame.mixer.music.play()

    # Aguarda até que a reprodução do áudio termine
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # Define uma taxa de atualização de 10 milissegundos

    # Limpa o mixer e encerra o pygame
    pygame.mixer.quit()
    pygame.quit()

def traduzir_texto(texto, idioma_origem, idioma_destino):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": idioma_origem,
        "tl": idioma_destino,
        "dt": "t",
        "q": texto
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        traducao = response.json()
        texto_traduzido = traducao[0][0][0] if traducao and traducao[0] and traducao[0][0] else texto
        return texto_traduzido
    else:
        print("Erro ao traduzir texto")
        return texto

def traduzir_texto_portugues(texto):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": 'en',
        "tl": 'pt',
        "dt": "t",
        "q": texto
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        traducao = response.json()
        texto_traduzido = traducao[0][0][0] if traducao and traducao[0] and traducao[0][0] else texto
        return texto_traduzido
    else:
        print("Erro ao traduzir texto")
        return texto

def enviar_para_api(text):
    url = 'http://localhost:11434/api/generate'
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "phi",
        "prompt": text,
        "format": "json",
        "stream": False
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Erro ao enviar solicitação para a API")
        return None


def resposta_api_falada(resposta_api):
    if resposta_api and 'response' in resposta_api:
        response_data = json.loads(resposta_api['response'])
        if response_data :
            print(json.dumps(response_data))
            mensagem = response_data['greeting'] if response_data.get('greeting') else response_data['response']
            filename = 'audio_saida'
            print("Resposta da API:", mensagem)
            texto_para_audio(mensagem, filename)
            reproduzir_audio(mensagem)
        else:
            print("Resposta da API não contém texto.")
    else:
        print("Resposta da API inválida.")

# Listar microfones disponíveis
print("Microfones disponíveis:")
listar_microfones_disponiveis()

# Selecionar microfone pelo índice
indice_microfone = int(input("Digite o índice do microfone que deseja usar: "))
microfone = selecionar_microfone(indice_microfone)

while True:
    texto = ouvir(microfone)
    if texto:
        print("Texto reconhecido:", texto)
        texto_traduzido = traduzir_texto(texto, 'pt', 'en')
        print("Texto traduzido para inglês:", texto_traduzido)
        response_api = enviar_para_api(texto_traduzido)
        resposta_api_falada(response_api)
