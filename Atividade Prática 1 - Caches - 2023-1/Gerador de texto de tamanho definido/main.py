import requests
import PyPDF2


default_folder = "result"
link_book = "https://www.gutenberg.org/files/62383/62383-0.txt"
file_name = "biblia-sagrada.txt"

outfile_name = "arquivo"
outfile_ext = "txt"
outfile_words = 1000

file_counter_stop = 100

# Baixando arquivo
# with open(default_folder + "/" + file_name, "wb") as file:
#     file.write(requests.get(link_book, allow_redirects=True).content)
#     file.close()


# Extraindo os dados
text = ""
with open(default_folder + "/" + file_name, "r", encoding="UTF-8") as file:
    text = file.read()

total_words = text.count(" ")

# Gera os arquivos com ~1000 palavras cada
word_counter = 0
file_counter = 1
while word_counter < total_words:
    with open(default_folder + "/" + f"{outfile_name}{file_counter:03}.{outfile_ext}", "w", encoding="UTF-8") as file:
        for i in range(outfile_words):
            skip = text.find(" ") + 1
            file.write(text[0:skip])
            text = text[skip:]
            word_counter += 1
        file.close()
    if file_counter >= file_counter_stop:
        break
    file_counter += 1

print(total_words, file_counter)
