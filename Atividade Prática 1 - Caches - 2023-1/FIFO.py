from tools import *

# Código para FIFO (First In First Out)
from queue import Queue


FIFO_cacheIndex = Queue(MAX_CACHE_SIZE)  # Fila com índices em ordem da fila do cache
FIFO_cache = Queue(MAX_CACHE_SIZE)  # Cache do programa


# Reinicializa as variáveis do cache
def FIFO_restartCache():
  global FIFO_cacheIndex, FIFO_cache
  FIFO_cacheIndex = Queue(MAX_CACHE_SIZE)
  FIFO_cache = Queue(MAX_CACHE_SIZE)


# Retorna se o arquivo está no cache
def FIFO_isFileInCache(index):
  isFileInCache = False  # CACHE MISS
  cacheIndexTemp = Queue(MAX_CACHE_SIZE)

  while not FIFO_cacheIndex.empty():
    itemKey = FIFO_cacheIndex.get()
    cacheIndexTemp.put(itemKey)
    if itemKey == index:  # CACHE HIT
      isFileInCache = True
  
  while not cacheIndexTemp.empty():
    FIFO_cacheIndex.put(cacheIndexTemp.get())
  
  return isFileInCache


# Retorna o arquivo no cache
def FIFO_getFileInCache(index):
  file = ""
  cacheIndexTemp = Queue(MAX_CACHE_SIZE)
  cacheTemp = Queue(MAX_CACHE_SIZE)

  while not FIFO_cacheIndex.empty():
    itemKey = FIFO_cacheIndex.get()
    itemValue = FIFO_cache.get()
    if itemKey == index:
      file = itemValue
    else:
      cacheIndexTemp.put(itemKey)
      cacheTemp.put(itemValue)

  FIFO_cacheIndex.put(index)
  FIFO_cache.put(file)
  while not cacheIndexTemp.empty():
    FIFO_cacheIndex.put(cacheIndexTemp.get())
    FIFO_cache.put(cacheTemp.get())

  return file


# Adiciona o arquivo ao cache
def FIFO_addFileInCache(index, file):
  cacheIndexTemp = Queue(MAX_CACHE_SIZE)
  cacheTemp = Queue(MAX_CACHE_SIZE)

  while not FIFO_cacheIndex.empty():
    itemKey = FIFO_cacheIndex.get()
    itemValue = FIFO_cache.get()
    if not cacheIndexTemp.full():
      cacheIndexTemp.put(itemKey)
      cacheTemp.put(itemValue)

  FIFO_cacheIndex.put(index)
  FIFO_cache.put(file)
  while not cacheIndexTemp.empty() and not FIFO_cacheIndex.full():
    FIFO_cacheIndex.put(cacheIndexTemp.get())
    FIFO_cache.put(cacheTemp.get())


# Retorna o arquivo diretamente do cache ou resgata ele do disco
def FIFO_getFile(index):
  curFileName = createFileName(index)
  text = ""
  isCacheMiss = False
  if not FIFO_isFileInCache(index):
    with open(curFileName, "r", encoding="UTF-8") as file:
      text = file.read()
      file.close()
    FIFO_addFileInCache(index, text)
    isCacheMiss = True
  else:
    text = FIFO_getFileInCache(index)
  return text, isCacheMiss
