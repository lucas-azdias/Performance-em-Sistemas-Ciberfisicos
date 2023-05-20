# Variáveis e funções bases para o código.
DEFAULT_FOLDER = "content" # Pasta padrão para os arquivos na máquina virtual
FILE_NAME = "arquivo" # Nome base dos arquivos
FILE_EXT = "txt" # Extensão base dos arquivos
FILE_QUANTITY = 100 # Quantidade total dos arquivos

MAX_CACHE_SIZE = 10 # Tamanho máximo do cache

# Retorna o nome do arquivo de acordo com o índice
def createFileName(index):
   return f"{FILE_NAME}{index:03}.{FILE_EXT}"
