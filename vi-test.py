import speech_recognition as sr
import pandas as pd
import pyttsx3
from fuzzywuzzy import fuzz
import pygame
import tempfile

# Carregar a tabela de perguntas e respostas em um DataFrame
df = pd.read_csv('database.csv', sep=';')

# Configurar o reconhecimento de fala
r = sr.Recognizer()

# Inicializar o Pygame
pygame.init()
clock = pygame.time.Clock()

# Configurações da janela
width, height = 277, 408
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Boca Animada")

# Carregar os frames da boca
frames = []
for i in range(5):
    frame = pygame.image.load(f"img/char-{i}.png")
    frames.append(frame)

# Definir a taxa de atualização dos frames
frame_rate = 10  # Quantos frames por segundo

mouth_frame = frames[0]
window.blit(mouth_frame, (0, 0))
pygame.display.flip()

def reproduzir_frase(frase):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_filename = tmp_file.name

    # Converter a resposta em áudio e reproduzir
    engine = pyttsx3.init()
    engine.save_to_file(frase, tmp_filename)
    engine.runAndWait()

    # Animar a boca enquanto o áudio resposta é reproduzido
    # Calcular o tempo de exibição de cada frame
    frame_duration = 1000 / frame_rate  # Tempo em milissegundos

    # Reproduzir o áudio resposta com o pygame
    pygame.mixer.music.load(tmp_filename)
    pygame.mixer.music.play()

    frame_index = 0
    elapsed_time = 0

    while pygame.mixer.music.get_busy():
        dt = clock.tick(30)

        elapsed_time += dt
        if elapsed_time >= frame_duration:
            # Atualizar a exibição do frame
            frame_index = (frame_index + 1) % len(frames)
            mouth_frame = frames[frame_index]
            window.blit(mouth_frame, (0, 0))
            pygame.display.flip()

            elapsed_time = 0

    pygame.mixer.music.stop()
    mouth_frame = frames[0]
    window.blit(mouth_frame, (0, 0))
    pygame.display.flip()

    if (frase == "Ok, até logo!"):
        pygame.quit()

continuar = True

reproduzir_frase("Olá! Como posso ajudá-lo?")

while continuar:
    with sr.Microphone() as source:
        print("Faça sua pergunta:")
        audio = r.listen(source)

    # Converter a fala em texto
    try: 
        pergunta = r.recognize_google(audio, language='pt-BR')
    except sr.UnknownValueError:
        reproduzir_frase("Desculpe, não entendi. Pode refazer a pergunta?")
        continue

    # Imprimir a pergunta
    print("Sua pergunta:", pergunta)

    if (pergunta.lower() == "terminar operação"):
        resposta = "Ok, até logo!"
        continuar = False
    else:
        # Verificar se a pergunta existe na tabela
        resposta = None
        for index, row in df.iterrows():
            similaridade = fuzz.ratio(pergunta.lower(), row['Perguntas'].lower())
            if similaridade >= 70:  # Similaridade da pergunta feita com a tabela
                resposta = row['Respostas']
                break
    
    if (resposta is None):
        resposta = "Infelizmente não possuo a informação necessária para responder a essa pergunta."
    
    reproduzir_frase(resposta)