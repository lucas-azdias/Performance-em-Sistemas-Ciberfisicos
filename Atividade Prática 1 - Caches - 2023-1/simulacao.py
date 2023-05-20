from tools import *
from simulacao import *
from LRU import *
from LFU import *
from FIFO import *

# Função do Modo de Simulação
from numpy.random import poisson
from random import randint, random
from time import time_ns

# Modo de simulação dos algoritimos de cache com três usuários
def modoSimulacao():
  totalTries = 200
  outputFileName = "output.txt"

  users = list()  # Lista com todas as tentativas de cada usuário fictício
  users.append([randint(1, FILE_QUANTITY)
               for _ in range(totalTries)])  # Aleatórios puros
  # Aleatórios com distribuição de Poisson
  users.append([int(poisson(FILE_QUANTITY / 2)) for _ in range(totalTries)])
  users.append(
      list())  # Aleatórios com peso para o intervalo de 30 a 40 de 33%
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

  # Lista com as informações de cada acesso a um arquivo de cada usuário para cada cache
  reportsCaches = list()

  # SIMULAÇÃO
  for c in range(len(getFileMethods)):  # Para cada tipo de cache
    getFileMethods[c][0]()  # Reinicia a memória de cache
    reportsCaches.append(list())

    for u in range(len(users)):  # Para cada tipo de usuário
      reportsCaches[c].append(list())
      meanDeltaTime = 0  # Média de latência
      amountCacheMiss = 0  # Quantidade de cache miss

      for i in range(totalTries):  # Para cada tentativa do usuário
        userTry = users[u][i]

        initialTime = time_ns()
        _, isCacheMiss = getFileMethods[c][1](userTry)
        endTime = time_ns()

        if isCacheMiss == True:
          amountCacheMiss += 1
        meanDeltaTime += endTime - initialTime

      meanDeltaTime /= totalTries

      # Dados do usuário no cache específico
      reportsCaches[c][u].extend(
          [meanDeltaTime, amountCacheMiss, totalTries - amountCacheMiss])

  # OUTPUT
  cacheNames = ["LRU", "LFU", "FIFO"]
  usersNames = ["Aleatórios puro", "Aleatórios com distribuição de Poisson",
                "Aleatórios com peso para o intervalo de 30 a 40 de 33%"]

  text = ""
  for c, cache in enumerate(reportsCaches):
    text += f"{cacheNames[c]}\n"
    for u, user in enumerate(cache):
      text += f"\tUser {u + 1} - {usersNames[u]}\n"
      text += f"\t\tMédia de latência: {user[0]}ns\n"
      text += f"\t\tQuantidade de cache miss: {user[1]}\n"
      text += f"\t\tQuantidade de cache hit: {user[2]}\n\n"
    text += "\n"

  with open("../" + outputFileName, "w", encoding="UTF-8") as file:
    file.write(text)
    file.close()
