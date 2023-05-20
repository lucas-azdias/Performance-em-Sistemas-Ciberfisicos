from tools import *

# Código para LFU (Least Frequently Used)
LFU_cacheFreqTable = dict()  # Planilha para associar o número dos arquivos com a frequência deles
LFU_cache = dict()  # Cache do programa


# Reinicializa as variáveis do cache
def LFU_restartCache():
  global LFU_cacheFreqTable, LFU_cache
  LFU_cacheFreqTable = dict()
  LFU_cache = dict()


# Retorna se o arquivo está no cache
def LFU_isFileInCache(index):
  if index in LFU_cache.keys():  # CACHE HIT
    return True
  else:  # CACHE MISS
    return False


# Retorna o arquivo no cache
def LFU_getFileInCache(index):
  LFU_cacheFreqTable[index] += 1
  return LFU_cache[index]


# Adiciona o arquivo ao cache
def LFU_addFileInCache(index, file):
  if len(LFU_cache) >= MAX_CACHE_SIZE:
    m = min(LFU_cacheFreqTable.values())
    for k, v in LFU_cacheFreqTable.items():
      if v == m:
        LFU_cacheFreqTable.pop(k)
        LFU_cache.pop(k)
        break

  LFU_cacheFreqTable[index] = 1
  LFU_cache[index] = file


# Retorna o arquivo diretamente do cache ou resgata ele do disco
def LFU_getFile(index, debug=False):
  curFileName = createFileName(index)
  text = ""
  isCacheMiss = False
  if not LFU_isFileInCache(index):
    with open(curFileName, "r", encoding="UTF-8") as file:
      text = file.read()
      file.close()
    LFU_addFileInCache(index, text)
    isCacheMiss = True
  else:
    text = LFU_getFileInCache(index)
  return text, isCacheMiss
