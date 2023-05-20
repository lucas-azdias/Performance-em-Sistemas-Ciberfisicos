from tools import *

# Código para LRU (Least Recently Used)
from collections import deque


LRU_cacheHashTable = dict()  # Planilha para associar o número dos arquivos com o índice no cache
LRU_cache = deque()  # Cache do programa


# Reinicializa as variáveis do cache
def LRU_restartCache():
  global LRU_cacheHashTable, LRU_cache
  LRU_cacheHashTable = dict()
  LRU_cache = deque()


# Retorna se o arquivo está no cache
def LRU_isFileInCache(index):
  if index in LRU_cacheHashTable.keys():  # CACHE HIT
    return True
  else:  # CACHE MISS
    return False


# Retorna o arquivo no cache
def LRU_getFileInCache(index):
  i = LRU_cacheHashTable[index]

  LRU_cache.appendleft(LRU_cache[i])
  LRU_cache.rotate(-(i + 1))
  LRU_cache.popleft()
  LRU_cache.rotate((i + 1))

  for key, value in LRU_cacheHashTable.items():
    if value < i:
      LRU_cacheHashTable[key] += 1

  LRU_cacheHashTable[index] = 0

  return LRU_cache[0]


# Adiciona o arquivo ao cache
def LRU_addFileInCache(index, file):
  if len(LRU_cache) >= MAX_CACHE_SIZE:
    i = list(LRU_cacheHashTable.values()).index(len(LRU_cache) - 1)
    LRU_cacheHashTable.pop(list(LRU_cacheHashTable.keys())[i])
    LRU_cache.pop()

  LRU_cache.appendleft(file)

  for key in LRU_cacheHashTable.keys():
    LRU_cacheHashTable[key] += 1

  LRU_cacheHashTable[index] = 0


# Retorna o arquivo diretamente do cache ou resgata ele do disco
def LRU_getFile(index):
  curFileName = createFileName(index)
  text = ""
  isCacheMiss = False
  if not LRU_isFileInCache(index):
    with open(curFileName, "r", encoding="UTF-8") as file:
      text = file.read()
      file.close()
    LRU_addFileInCache(index, text)
    isCacheMiss = True
  else:
    text = LRU_getFileInCache(index)
  return text, isCacheMiss
