from random import randint
from tools import *
from LRU import *
from LFU import *
from FIFO import *

# Baixando os arquivos de texto para a máquina virtual a partir do meu GitHub.
import requests
import os


# Path para os arquivos salvos no meu GitHub
PATH = "https://raw.githubusercontent.com/FunNyLuAz/Performance-em-Sistemas-Ciberfisicos/main/Atividade%20Pr%C3%A1tica%201%20-%20Caches%20-%202023-1/1000_words_files/"

folderPath = os.path.join(os.getcwd(), DEFAULT_FOLDER)
if not os.path.exists(folderPath):
  os.makedirs(DEFAULT_FOLDER)
os.chdir(folderPath)
"""
print("\nBaixando arquivos do GitHub...")
for i in range(FILE_QUANTITY):
  curFileName = createFileName(i + 1)
  with open(curFileName, "wb") as file:
    file.write(requests.get(PATH + curFileName, allow_redirects=True).content)
    file.close()
  print(f"{curFileName} baixado.")
print("\nArquivos baixados com sucesso.")
"""

# Programa principal
from numpy.random import poisson
from random import randint, random
from time import time_ns


# Imprime arquivo solicitado na tela
def printTextFile(index, text):
  curFileName = createFileName(index)
  print(f"\n###{curFileName.upper()}###\n" + text + f"\n###{'#' * len(curFileName)}###")


# Modo de simulação dos algoritimos de cache com três usuários
def modoSimulacao():
  totalTries = 200
  outputFileName = "output.txt"

  users = list()  # Lista com todas as tentativas de cada usuário fictício
  users.append([randint(1, FILE_QUANTITY) for _ in range(totalTries)])  # Aleatórios puros
  users.append([int(poisson(FILE_QUANTITY / 2)) for _ in range(totalTries)])  # Aleatórios com distribuição de Poisson
  users.append(list())  # Aleatórios com peso para o intervalo de 30 a 40 de 33%
  for _ in range(totalTries):
    if random() > 1/3:
      n = randint(1, FILE_QUANTITY - 11)
      if n >= 30:
        n += 11  # São onze valores bloqueados (30, 31, ..., 40)
      users[len(users) - 1].append(n)
    else:
      users[len(users) - 1].append(randint(30, 40))

  getFileMethods = [  # Lista para permitir iterar pelos métodos de cada cache
    (LRU_restartCache, LRU_getFile),
    (LFU_restartCache, LFU_getFile),
    (FIFO_restartCache, FIFO_getFile),
  ]

  reportsCaches = list()  # Lista com as informações de cada acesso a um arquivo de cada usuário para cada cache

  for c in range(len(getFileMethods)): # Para cada tipo de cache
    getFileMethods[c][0]()  # Reinicia a memória de cache
    reportsCaches.append(list())
    for u in range(len(users)):  # Para cada tipo de usuário
      reportsCaches[c].append(list())
      for i in range(totalTries):  # Para cada tentativa do usuário
        userTry = users[u][i]
        initialTime = time_ns()
        _, isCacheMiss = getFileMethods[c][1](userTry)
        endTime = time_ns()
        reportsCaches[c][u].append((i + 1, userTry, endTime - initialTime, isCacheMiss))

  # OUTPUT
  cacheNames = ["LRU", "LFU", "FIFO"]
  usersNames = ["Aleatórios puro", "Aleatórios com distribuição de Poisson", "Aleatórios com peso para o intervalo de 30 a 40 de 33%"]
  completeText = "\nLOG DE CADA TENTATIVA:\n"  # Armazena o texto com os detalhes de cada tentativa de usuário

  with open("../" + outputFileName, "w", encoding="UTF-8") as file:

    for c, cache in enumerate(reportsCaches):

      text = f"{cacheNames[c]}\n"
      file.write(text)
      completeText += text

      for u, user in enumerate(cache):

        text = f"\tUser {u + 1} - {usersNames[u]}\n"
        file.write(text)
        completeText += text

        meanDeltaTime = 0
        amountCacheMiss = 0

        completeText += f"\t\t{'INDEX':5} \t {'ARQUIVO':7} \t {'LATÊNCIA (ns)':>17} \t {'ISCACHEMISS':>11}\n"
        for index in user:
          if index[3] == True:
            amountCacheMiss += 1
          meanDeltaTime += index[2]
          completeText += f"\t\t{index[0]:>5} \t {index[1]:>7} \t {index[2]:>17} \t {'True' if index[3] else 'False':>11}\n"
        completeText += "\n\n"

        meanDeltaTime /= totalTries

        text = f"\t\tMédia de latência: {meanDeltaTime}ns\n"
        text += f"\t\tQuantidade de cache miss: {amountCacheMiss}\n"
        text += f"\t\tQuantidade de cache hit: {totalTries - amountCacheMiss}\n\n"
        file.write(text)
      
      text = "\n"
      file.write(text)
      completeText += text
    
    file.write(completeText)
    file.close()


while True:
  print("""

Selecione a opção de cache principal:
1 - LRU (Least Recently Used)
2 - LFU (Least Frequently Used)
3 - FIFO (First In First Out)
""")
  mainCacheOption = input(" > ")  # 1 - LRU | 2 - LFU | 3 - FIFO
  if mainCacheOption.isdigit():
    mainCacheOption = int(mainCacheOption)
    break

getFile = None
match mainCacheOption:  # Seleciona a função principal para o cache de acordo com sua escolha
  case 1:
    getFile = LRU_getFile
  case 2:
    getFile = LFU_getFile
  case 3:
    getFile = FIFO_getFile
  case _:
    print("Não especificado algoritmo de cache.")
    exit()

# Loop da UI
print("\n\nIniciando programa...\n\nPrograma de solicitação de textos com cache\n")
while True:
  msg = input(" > ")

  if msg.lstrip('-').isdigit():
    msg = int(msg)
    if msg == 0:
      print("Programa encerrado.")
      break
    elif msg == -1:
      print("Modo de simulação iniciado...")
      modoSimulacao()
    elif 1 <= msg <= FILE_QUANTITY:
      print(f"Solicitando {createFileName(msg)}...")
      text, _ = getFile(msg)
      printTextFile(msg, text)
    else:
      print("Valor inválido.")
  else:
    print("Entrada inválida.")
  print()
