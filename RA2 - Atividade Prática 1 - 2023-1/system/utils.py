from math import log2

from bitarray import bitarray


MAIN_MEMORY_SIZE = 2**10 * 2**10  # Main memory with 1MB (1024KB)
VIRTUAL_MEMORY_SIZE = 100 * 2**10  # Virtual Memory with 100KB
PAGE_SIZE = 4 * 2**10  # Page with 4KB
WORD_SIZE = 1  # Word with 1B (8 bits)

PAGE_AMOUNT = MAIN_MEMORY_SIZE // PAGE_SIZE  # Amount of pages in the main memory
WORD_AMOUNT = PAGE_SIZE // WORD_SIZE  # Amount of words in each page

PAGE_ADDRESS_SIZE = int(log2(PAGE_AMOUNT)) if int(log2(PAGE_AMOUNT)) >= 8 else 8  # Size of the page address
OFFSET_ADDRESS_SIZE = int(log2(WORD_AMOUNT))  # Size of the offset address
ADDRESS_SIZE = PAGE_ADDRESS_SIZE + OFFSET_ADDRESS_SIZE  # Size of the entire address


def int_to_bytes(i:int, length:int) -> bytes:
    return i.to_bytes(length, 'big')


def bytes_to_int(b:bytes) -> int:
    return int.from_bytes(b, 'big')


def int_page_address_to_bytes(addr:int) -> bytes:
    b = bin(addr)[2:]
    size = len(b) // PAGE_ADDRESS_SIZE + 1
    addr_bytes = bitarray('0' * (size * PAGE_ADDRESS_SIZE - len(b)) + b).tobytes()
    return addr_bytes


def int_offset_address_to_bytes(offset: int) -> bytes:
    b = bin(offset)[2:]
    offset_bytes = bitarray('0' * (OFFSET_ADDRESS_SIZE - len(b)) + b).tobytes()
    return offset_bytes


def int_address_to_bytes(addr:int, offset: int) -> bytes:
    ba = bin(addr)[2:]
    bo = bin(offset)[2:]
    size = len(ba) // PAGE_ADDRESS_SIZE + 1
    addr_bytes = bitarray('0' * (size * PAGE_ADDRESS_SIZE + OFFSET_ADDRESS_SIZE - len(ba + bo)) + ba + bo).tobytes()
    return addr_bytes


def get_amount_offsets_by_bits(content_bits_len) -> int:
    offsets_amount = content_bits_len // (WORD_SIZE * 8)
    left = 1 if offsets_amount != content_bits_len / (WORD_SIZE * 8) else 0
    return offsets_amount + left


def get_amount_offsets_by_bytes(content_bytes_len) -> int:
    offsets_amount = content_bytes_len // WORD_SIZE
    left = 1 if offsets_amount != content_bytes_len / WORD_SIZE else 0
    return offsets_amount + left
