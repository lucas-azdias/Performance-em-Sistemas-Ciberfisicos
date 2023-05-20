from system import MMU, VirtualMemory, bytes_to_int, VIRTUAL_MEMORY_SIZE, PAGE_SIZE, PAGE_AMOUNT

from io import BufferedReader
from math import ceil, log2
from os import remove
from random import randint, shuffle
from requests import get
from sys import stdout
from time import time_ns


__LINK_TEST_FILE = "https://www.gutenberg.org/files/62383/62383-0.txt"  # Link for downloading the test file
__TEST_FILENAME = "arquivo.txt"


def test():
    # Tests the fragmentation of the main memory and the sequencial form of the virtual memory
    # and also the reliability of the data in the memory and the use of the swap memory (when the main memory gets full)
    swap_filename = "test_swap.bin"
    mmu = MMU(swap_filename)
    vms = list()

    def print_delta_time(point_time):
        # Prints the difference in time formatted
        print(f"{round((time_ns() - point_time) / 1_000_000_000, 2)}s ({time_ns() - point_time}ns)")


    print("\nTesting...")


    # Downloading test file
    print("\nDownloading test file...")
    point_time = time_ns()

    test_file = __get_test_file()

    print_delta_time(point_time)


    # Generating text blocks for each virtual memory in different sizes and quantities
    print("\nGenerating text blocks for each virtual memory in different sizes and quantities...")
    point_time = time_ns()

    text_blocks = list()

    needed_pages = (PAGE_AMOUNT + 5)
    cur_page = 0
    cur_vm = 0
    while (cur_page < needed_pages):
        vms.append(VirtualMemory(cur_vm + 1, mmu))

        sorted_pages = randint((VIRTUAL_MEMORY_SIZE // PAGE_SIZE) // 2, (VIRTUAL_MEMORY_SIZE // PAGE_SIZE))
        for _ in range(sorted_pages):
            sorted_size = randint(PAGE_SIZE // 2, PAGE_SIZE)
            text_blocks.append((cur_vm, test_file.read(sorted_size), sorted_size))

        cur_page += sorted_pages
        cur_vm += 1

    print_delta_time(point_time)
    

    # Putting the text blocks in each virtual memory in random order
    print("\nPutting the text blocks in each virtual memory in random order...")
    point_time = time_ns()

    vms_last_index = [0 for _ in range(cur_vm)]

    shuffle(text_blocks)
    for text_block in text_blocks:
        index = vms_last_index[text_block[0]]
        vms[text_block[0]].set(index, text_block[1])
        vms_last_index[text_block[0]] += 1
        

    print_delta_time(point_time)
    

    # Generating table of pages in memory
    print("\nGenerating table of pages in memory...")
    point_time = time_ns()

    def generate_page_address_binary(integer):
        # Generates the page address formatted in binary for plotting in the table
        b = bin(integer)[2:]
        return '0' * (ceil(log2(cur_page)) - len(b)) + b + f" ({integer})"

    pages_table = [
        (
            generate_page_address_binary(bytes_to_int(k)),
            "main" if bytes_to_int(k) < PAGE_AMOUNT else "swap",
            "free" if v else "used"
        ) for k, v in mmu.get_pages_table().items()
    ]
    __print_table(["Main address", "Type", "Status"], pages_table)

    print_delta_time(point_time)
    input("\n> Press <enter> to continue")


    # Generating table of pages for each virtual memory
    print("\nGenerating table of pages for each virtual memory...")
    point_time = time_ns()

    isAllUnique = True
    seen_main_addr = list()

    processes_table = mmu.get_processes_table()
    for id_vm, link_table in processes_table.items():
        new_link_table =[
            (
                generate_page_address_binary(bytes_to_int(k)),
                generate_page_address_binary(bytes_to_int(v))
            ) for k, v in link_table.items()
        ]
        __print_table(["Virtual address", "Main address"], new_link_table, "VM ID " + str(id_vm), hasTitle=True)
        for v in link_table.values():
            if not v in seen_main_addr:
                seen_main_addr.append(v)
            else:
                isAllUnique = False

    if isAllUnique:
        print("All main memory addresses registred are unique.")
    else:
        print("ERROR! Not all main memory addresses registred are unique.")


    print_delta_time(point_time)
    input("\n> Press <enter> to continue")


    test_file.close()
    remove(__TEST_FILENAME)

    print("\n\nTests ended.")


def __get_test_file() -> BufferedReader:
    # Downloads a test file from the web and returns it
    with open(__TEST_FILENAME, "wb") as file:
        response = get(__LINK_TEST_FILE, stream=True)
        length = response.headers.get('content-length')

        if length is None:
            raise FileNotFoundError("Test file could not be downloaded")
        else:
            length = int(length)
            downloaded_length = 0
            for data in response.iter_content(chunk_size=4096):
                downloaded_length += len(data)
                file.write(data)
                stdout.write(f"\r{round(downloaded_length / 1_000_000, 2):.2f}MB/{round(length / 1_000_000, 2):.2f}MB")
                stdout.flush()
            print()
        
        file.close()

    return open(__TEST_FILENAME, "rb")


def __print_table(headers:tuple, items:tuple, title="", hasTitle=False):
    # Prints a formatted table of values
    sep_size = 3  # Size of separator in table

    items_size = list()  # Size for each column
    for i, header in enumerate(headers):  # Determines the greatest size for each column
        val = 0
        for item in items:
            if len(str(item[i])) > val:
                val = len(str(item[i]))
        if val < len(str(header)):
            val = len(str(header))
        items_size.append(val)

    # Total length of the table line
    length = sum(items_size) + (len(items_size) - 1) * sep_size

    # Lambda function for ploting corretly each column value in the table
    put_value = lambda s, l: str(s) + ' ' * (l - len(str(s)))

    # TABLE HEADER
    text = ""
    text += f"╒═{'═' * length}═╕\n"

    if hasTitle:  # Puts title if it's enabled
        text += f"│ {put_value(title, length)} │\n"
        text += f"╞═{'═' * length}═╡\n"

    text += "│ "
    for i, header in enumerate(headers):  # Puts the header of each column
        text += put_value(header, items_size[i])
        if i < len(headers) - 1:
            text += " " * sep_size
    text += f" │\n╞═{'═' * length}═╡\n"
    # END TABLE HEADER

    # TABLE BODY
    for item in items:  # Puts the value of each column
        text += "│ "
        for i, e in enumerate(item):
            text += put_value(e, items_size[i])
            if i < len(item) - 1:
                text += " " * sep_size
        text += " │\n"

    text += f"└─{'─' * length}─┘"
    # END TABLE BODY

    print(text)
