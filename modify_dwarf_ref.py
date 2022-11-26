import sys
import io
from elftools.elf.elffile import ELFFile

SRC_PATH = 'intof'
DST_PATH = 'intof_mod'

# see section section 6.2.5.1 in DWARF4 spec
FWD_OPCODE = (1 + 5 + 14 * 4 + 13).to_bytes(1, 'little', signed=False)
BWD_OPCODE = (-1 + 5 + 14 * 4 + 13).to_bytes(1, 'little', signed=False)
NOPCODE = (0 + 5 + 14 * 0 + 13).to_bytes(1, 'little', signed=False)
# NOPCODE = b'\x00'


def replace_filename(bin_data: bytes):
    return bin_data.replace(b'intof.c', b'dummy.c')


def get_line_prog(elf):
    dwarf = elf.get_dwarf_info()
    cu = list(dwarf.iter_CUs())[0]
    return dwarf.line_program_for_CU(cu)


def get_main_addr(elf):
    symtab = elf.get_section_by_name('.symtab')
    main = symtab.get_symbol_by_name('main')[0]
    return main.entry.st_value


def modify_dwarf(bin_data: bytes):
    start = bin_data.find(b'\x4B' * 20)
    end = bin_data.rfind(b'\x4B' * 20) + 20
    # if end - start != 1024:
    #     print('replacement length:', end - start, start, end, file=sys.stderr)

    replacement = (FWD_OPCODE + BWD_OPCODE) * int(1022 / 2) + FWD_OPCODE * 2
    data = bin_data[0:start] + replacement + bin_data[end:]

    elf = ELFFile(io.BytesIO(data))
    dwarf = elf.get_dwarf_info()
    lineprog = get_line_prog(elf)
    offset = dwarf.debug_line_sec.global_offset + lineprog.program_start_offset
    set_addr = b'\x05\x01\x00\x09\x02' + (get_main_addr(elf) + 0x12).to_bytes(8, 'little')
    data = data[0:offset] + set_addr + NOPCODE * (start - offset - len(set_addr)) + data[start:]
    return replace_filename(data)


def main():
    # with open('intof', 'rb') as f:
    #     bin_data = f.read()
    # data = modify_dwarf(sys.stdin.buffer.read())
    # sys.stdout.buffer.write(data)
    with open(SRC_PATH, 'rb') as f:
        data = modify_dwarf(f.read())
    with open(DST_PATH, 'wb') as f:
        f.write(data)


if __name__ == '__main__':
    main()
