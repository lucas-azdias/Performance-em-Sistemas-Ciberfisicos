from tools import *
from simulacao import *
from LRU import *
from LFU import *
from FIFO import *

# Baixando os arquivos de texto para a máquina virtual a partir do meu GitHub.
import requests
import os


# Path para os arquivos salvos no meu GitHub
PATH = "https://raw.githubusercontent.com/FunNyLuAz/Performance-em-Sistemas-Ciberfisicos/main/Atividade%20Pr%C3%A1tica%201%20-%20Caches%20-%202023-1/1000_words_files/"

if os.path.basename(os.getcwd()) != DEFAULT_FOLDER:
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
# Imprime arquivo solicitado na tela
def printTextFile(index, text):
  curFileName = createFileName(index)
  print(f"\n###{curFileName.upper()}###\n" + text + f"\n###{'#' * len(curFileName)}###")


# Seleção do cache principal
while True:
  print("""Selecione a opção de cache principal:
1 - LRU (Least Recently Used)
2 - LFU (Least Frequently Used)
3 - FIFO (First In First Out)
""")
  mainCacheOption = input(" > ")  # 1 - LRU | 2 - LFU | 3 - FIFO
  if mainCacheOption.isdigit():
    mainCacheOption = int(mainCacheOption)
    break

getFile = None
if mainCacheOption == 1:  # Seleciona a função principal para o cache de acordo com sua escolha
  getFile = LRU_getFile
elif mainCacheOption == 2:
  getFile = LFU_getFile
elif mainCacheOption == 3:
  getFile = FIFO_getFile
else:
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
