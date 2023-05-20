from system.utils import *

from os import remove


class MMU:
    # DATA STRUCTURES OF THE MMU
    __processes_table = None  # Nested dicts thats links each virtual memory ID with their dicts
                            # (each virtual memory dict links the virtual memory address with
                            # its main memory address)
                            # {id_virtual_memory:{addr_virtual_memory:addr_main_memory}}
    __pages_table = None  # Dict thats links each main memory address (page address) with its
                        # current status of use
                        # {addr_main_memory:isFree}
    
    # MAIN MEMORY VARIABLES
    __memory = None  # Bitarray that stores the data
    __memory_swap_filename = None  # Filename of the swap memory file


    def __init__(self, memory_swap_filename):
        # MMU Constructor
        self.__processes_table = dict()
        self.__pages_table = dict()
        self.__memory = bitarray('0' * MAIN_MEMORY_SIZE * 8)
        self.__memory_swap_filename = memory_swap_filename
        
        for i in range(PAGE_AMOUNT):  # Initializing pages_table with every page free
            self.__pages_table[int_page_address_to_bytes(i)] = True

        with open(memory_swap_filename, "wb") as swap_memory:  # Initializing swap memory file
            swap_memory.close()


    def __del__(self):
        # MMU Destructor
        remove(self.__memory_swap_filename)


    # -- START INTERFACE --
    def add_mem_virtual(self, id_mem_virtual:int):
        # Register a new virtual memory in the registry
        if not id_mem_virtual in self.__processes_table:
            self.__processes_table[id_mem_virtual] = dict()
        else:
            raise ValueError("Virtual memory already registered")


    def get_content(self, id_virtual_memory:int, addr_virtual_memory:bytes, offset_start:int=0, offsets:int=1) -> bytes:
        # Read an entire content (can have multiple pages) in the main memory using the virtual memory address
        # Read the entire content in the memory
        content = bytearray()
        for i in range(offsets):
            page_addr = int_page_address_to_bytes(bytes_to_int(addr_virtual_memory) + i // WORD_AMOUNT)
            offset = offset_start + i - ((i // WORD_AMOUNT) * WORD_AMOUNT)
            # content += self.__get_word(id_virtual_memory, page_addr, offset=offset)
            content.extend(self.__get_word(id_virtual_memory, page_addr, offset=offset))
        return bytes(content)


    def set_content(self, id_virtual_memory:int, addr_virtual_memory:bytes, content:bytes, offset_start:int=0, offsets:int=0) -> int:  # offsets<=0 -> goes automatic
        # Write an entire content (can have multiple pages) in the main memory using the virtual memory address        
        content_bits = bitarray()
        content_bits.frombytes(content)

        if offsets <= 0:  # Makes automatic offsets mode
            offsets = get_amount_offsets_by_bits(len(content_bits))

        offsets_concluded = 0
        for i in range(offsets):
            page_addr = int_page_address_to_bytes(bytes_to_int(addr_virtual_memory) + i // WORD_AMOUNT)
            offset = offset_start + i - ((i // WORD_AMOUNT) * WORD_AMOUNT)

            cont_index = WORD_SIZE * 8 * i
            cont = content_bits[cont_index:(cont_index + WORD_SIZE * 8)].tobytes()

            result = self.__set_word(id_virtual_memory, page_addr, cont, offset=offset)

            if not result:
                break
            else:
                offsets_concluded += 1

        return offsets_concluded


    def dlt_content(self, id_virtual_memory:int, addr_virtual_memory:bytes, offset_start:int=0, offsets:int=1) -> bytes:
        # Delete an entire content (can have multiple pages) in the main memory using the virtual memory address (and unregister unused pages)
        # Delete the entire content in the memory
        offsets_deleted = self.set_content(id_virtual_memory, addr_virtual_memory, bytes(), offset_start, offsets)
        
        # Unregister every page that has been entirely deleted
        for addr_vm in self.__processes_table[id_virtual_memory].copy():
            cont = self.get_content(id_virtual_memory, addr_vm, offset_start=0, offsets=WORD_AMOUNT)
            if cont == bitarray('0' * PAGE_SIZE * 8).tobytes():
                self.__unregister_page(id_virtual_memory, addr_vm)
        
        return offsets_deleted
    

    def get_memory(self):
        # Getter of memory
        return self.__memory
    

    def get_processes_table(self):
        # Getter of processes_table
        return self.__processes_table
    

    def get_pages_table(self):
        # Getter of pages_table
        return self.__pages_table
    # -- END INTERFACE --


    def __get_word(self, id_virtual_memory:int, addr_virtual_memory:bytes, offset:int=0) -> bytes:
        # Read a word in the main memory using the virtual memory address
        addr_bytes = self.__get_memory_addr(id_virtual_memory, addr_virtual_memory, auto_creation=False)
        if addr_bytes == None:
            return bytes()
        else:
            addr = bytes_to_int(addr_bytes)

        # If valid, read only one word in the memory
        is_offset_valid = 0 <= offset < WORD_AMOUNT
        if self.__check_memory_addr(addr) and is_offset_valid:
            word_index = addr * PAGE_SIZE * 8 + offset * WORD_SIZE * 8
            return self.__memory[word_index:(word_index + WORD_SIZE * 8)][::-1].tobytes()
        elif is_offset_valid:
            word_index = (addr - PAGE_AMOUNT) * PAGE_SIZE * 8 + offset * WORD_SIZE * 8

            # Reads current content
            with open(self.__memory_swap_filename, "rb") as swap_memory:
                swap_memory.readline()
                cont = swap_memory.read()
                swap_memory.close()

            swap_memory_bits = bitarray()
            swap_memory_bits.frombytes(cont)

            return swap_memory_bits[word_index:(word_index + WORD_SIZE * 8)][::-1].tobytes()
        else:
            raise Exception("Main memory address invalid")


    def __set_word(self, id_virtual_memory:int, addr_virtual_memory:bytes, content:bytes, offset:int=0) -> bool:
        # Write a word in the main memory using the virtual memory address
        # Takes the address in the main memory if exists (if not creates a new one for it)
        addr_bytes = self.__get_memory_addr(id_virtual_memory, addr_virtual_memory)
        if addr_bytes == None:
            return False
        else:
            addr = bytes_to_int(addr_bytes)

        # If valid, write only one word in the memory
        content_bits = bitarray()
        content_bits.frombytes(content)

        is_offset_valid = 0 <= offset < WORD_AMOUNT
        if self.__check_memory_addr(addr) and is_offset_valid:
            word_index = addr * PAGE_SIZE * 8 + offset * WORD_SIZE * 8
            if (len(content_bits) < WORD_SIZE * 8):
                for _ in range(WORD_SIZE * 8 - len(content_bits)):
                    content_bits.append(0)
            self.__memory[word_index:(word_index + WORD_SIZE * 8)] = content_bits[WORD_SIZE * 8::-1]
            return True
        elif is_offset_valid:
            word_index = (addr - PAGE_AMOUNT) * PAGE_SIZE * 8 + offset * WORD_SIZE * 8

            # Reads current content
            with open(self.__memory_swap_filename, "rb") as swap_memory:
                line = swap_memory.readline()
                cont = swap_memory.read()
                swap_memory.close()

            swap_memory_bits = bitarray()
            swap_memory_bits.frombytes(cont)

            if (len(content_bits) < WORD_SIZE * 8):
                for _ in range(WORD_SIZE * 8 - len(content_bits)):
                    content_bits.append(0)
            
            swap_memory_bits[word_index:(word_index + WORD_SIZE * 8)] = content_bits[WORD_SIZE * 8::-1]

            # Writes the new content in the swap memory
            with open(self.__memory_swap_filename, "wb") as swap_memory:
                swap_memory.write(line)
                swap_memory.write(swap_memory_bits)
                swap_memory.close()
            
            return True
        else:
            return False


    def __check_memory_addr(self, addr_int:int) -> bool:
        # Verify is the address in the main memory is valid
        if addr_int < 0:
            raise ValueError("Negative address given")
        elif addr_int < PAGE_AMOUNT:
            return True
        else:
            return False
    

    def __get_memory_addr(self, id_virtual_memory: int, addr_virtual_memory: bytes, auto_creation=True) -> bytes:
        # Return main memory address linked to the virtual memory address given
        # Verifies if there is a dict of addresses for tha virtual memory given (if auto_creation, creates a new if none found)
        if not id_virtual_memory in self.__processes_table:
            raise ValueError("Virtual memory ID invalid")
        
        # Takes the address in the main memory if exists (if not returns None)
        if addr_virtual_memory in self.__processes_table[id_virtual_memory]:
            return self.__processes_table[id_virtual_memory][addr_virtual_memory]
        elif auto_creation and self.__is_virtual_memory_expandible(id_virtual_memory):  # Creates a new address
            addr = self.__next_memory_addr_free()
            if addr == None:
                addr = self.__create_swap_page()
            self.__register_page(id_virtual_memory, addr_virtual_memory, addr)
            return addr
        else:
            return None


    def __next_memory_addr_free(self) -> bytes:
        # Return next free address in the main memory
        for k, v in self.__pages_table.items():
            if v:
                return k
        return None


    def __is_virtual_memory_expandible(self, id_virtual_memory:int) -> bool:
        # Verifies if the virtual memory can be expanded
        if id_virtual_memory in self.__processes_table and len(self.__processes_table[id_virtual_memory]) >= VIRTUAL_MEMORY_SIZE // PAGE_SIZE:
            return False
        else:
            return True


    def __register_page(self, id_virtual_memory:int, addr_virtual_memory:bytes, addr_main_memory:bytes):
        # Register a page in the main memory for a virtual memory
        if self.__pages_table[addr_main_memory]:
            self.__processes_table[id_virtual_memory][addr_virtual_memory] = addr_main_memory
            self.__pages_table[addr_main_memory] = False
        else:
            raise ValueError("Address at use")


    def __unregister_page(self, id_virtual_memory:int, addr_virtual_memory:bytes):
        # Unregister a page in the main memory from a virtual memory
        addr_main_memory = self.__get_memory_addr(id_virtual_memory, addr_virtual_memory, auto_creation=False)
        if not self.__pages_table[addr_main_memory]:
            if self.__check_memory_addr(bytes_to_int(addr_main_memory)):
                self.set_content(id_virtual_memory, addr_virtual_memory, bitarray('0' * PAGE_SIZE * 8).tobytes(), 0, WORD_AMOUNT)
                self.__pages_table[addr_main_memory] = True
                self.__processes_table[id_virtual_memory].pop(addr_virtual_memory)
            else:
                self.__erase_swap_page(id_virtual_memory, addr_virtual_memory)
        else:
            raise ValueError("Address already free")


    def __create_swap_page(self) -> bytes:
        # Creates a new page in the swap memory
        # Reads current content
        with open(self.__memory_swap_filename, "rb") as swap_memory:
            lines = swap_memory.readlines()
            swap_memory.close()

        # Takes the current index of page in the swap memory (if no previous one, creates one)
        if len(lines) > 0:
            next_swap_page = int(lines[0][:-1])
        else:
            next_swap_page = 0
            lines.append(next_swap_page)
        
        # Updates content in the swap memory
        lines[0] = (str(next_swap_page + 1) + "\n").encode("utf-8")
        lines.append(bitarray('0' * PAGE_SIZE * 8).tobytes())
        
        # Writes the new content in the swap memory
        with open(self.__memory_swap_filename, "wb") as swap_memory:
            swap_memory.writelines(lines)
            swap_memory.close()

        # Adds the new memory address to the pages_table
        addr = int_page_address_to_bytes(PAGE_AMOUNT + next_swap_page)
        self.__pages_table[addr] = True

        # Return the new memory address
        return addr


    def __erase_swap_page(self, id_virtual_memory:int, addr_virtual_memory:bytes):
        # Erases an existing page in the swap memory
        addr = bytes_to_int(self.__get_memory_addr(id_virtual_memory, addr_virtual_memory, auto_creation=False))
        if self.__check_memory_addr(addr):
            return

        # Reads current content
        with open(self.__memory_swap_filename, "rb") as swap_memory:
            next_swap_page = int(swap_memory.readline()[:-1])
            cont = swap_memory.read()
            swap_memory.close()

        swap_memory_bits = bitarray()
        swap_memory_bits.frombytes(cont)
        word_index = (addr - PAGE_AMOUNT) * PAGE_SIZE * 8
        swap_memory_bits[word_index:] = swap_memory_bits[(word_index + PAGE_SIZE * 8):]

        # Updates content in the swap memory
        lines = ((str(next_swap_page - 1) + "\n").encode("utf-8"), swap_memory_bits)

        # Writes the new content in the swap memory
        with open(self.__memory_swap_filename, "wb") as swap_memory:
            swap_memory.writelines(lines)
            swap_memory.close()

        # Updates the addresses of swap memory
        for id_vm, addrs in self.__processes_table.items():
            for addr_vm, addr_mm in addrs.items():
                addr_mm_int = bytes_to_int(addr_mm)
                if addr_mm_int > addr:
                    self.__processes_table[id_vm][addr_vm] = int_page_address_to_bytes(addr_mm_int - 1)
        
        # Removes the current virtual memory address
        self.__processes_table[id_virtual_memory].pop(addr_virtual_memory)
