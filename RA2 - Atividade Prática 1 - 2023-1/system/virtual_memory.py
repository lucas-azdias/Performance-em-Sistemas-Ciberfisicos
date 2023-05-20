from system import MMU, int_page_address_to_bytes, PAGE_SIZE, VIRTUAL_MEMORY_SIZE


class VirtualMemory:
    id = None  # Virtual memory ID
    linked_mmu = None  # MMU of the virtual memory


    def __init__(self, id:int, mmu:MMU):
        # VirtualMemory Constructor
        self.id = id
        self.linked_mmu = mmu
        mmu.add_mem_virtual(id)
    

    def __del__(self):
        # VirtualMemory Destructor
        self.dlt(0, 0, VIRTUAL_MEMORY_SIZE // PAGE_SIZE)


    def get(self, addr:int, offset_start:int=0, offsets:int=1) -> bytes:
        # Read the content in the given virtual memory address
        if addr * PAGE_SIZE * 8 + offsets - offset_start < VIRTUAL_MEMORY_SIZE * 8:
            return self.linked_mmu.get_content(self.id, int_page_address_to_bytes(addr), offset_start=offset_start, offsets=offsets)
        else:
            return None


    def set(self, addr:int, content:bytes, offset_start:int=0, offsets:int=0) -> int:  # offsets<=0 -> goes automatic
        # Write the content in the given virtual memory address
        if addr * PAGE_SIZE * 8 + offsets - offset_start < VIRTUAL_MEMORY_SIZE * 8:
            return self.linked_mmu.set_content(self.id, int_page_address_to_bytes(addr), content, offset_start=offset_start, offsets=offsets)
        else:
            return 0


    def dlt(self, addr:int, offset_start:int=0, offsets:int=1) -> int:
        # Delete the content in the given virtual memory address
        if addr * PAGE_SIZE * 8 + offsets - offset_start < VIRTUAL_MEMORY_SIZE * 8:
            return self.linked_mmu.dlt_content(self.id, int_page_address_to_bytes(addr), offset_start=offset_start, offsets=offsets)
        else:
            return 0
