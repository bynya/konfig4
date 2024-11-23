import sys
import struct
import csv

MEMORY = [0] * 256
REGISTERS = [0] * 16

def load_const(dest_reg, value):
    REGISTERS[dest_reg] = value

def write_memory(offset, base_reg, source_reg):
    address = REGISTERS[base_reg] + offset
    MEMORY[address] = REGISTERS[source_reg]

def unary_popcnt(offset, base_reg, dest_reg):
    address = REGISTERS[base_reg] + offset
    value = MEMORY[address]
    REGISTERS[dest_reg] = bin(value).count('1')

def assemble(input_file, output_file, log_file):
    opcode_map = {
        "LOAD_CONST": 4,
        "WRITE_MEMORY": 6,
        "UNARY_POPCNT": 7,
    }

    binary_code = bytearray()
    log_entries = []

    with open(input_file, 'r') as asm_file:
        for line in asm_file:
            line = line.strip()
            if not line or line.startswith(";"):
                continue

            parts = line.split()
            command = parts[0]
            opcode = opcode_map[command]

            if command == "LOAD_CONST":
                _, reg, value = parts
                reg = int(reg)
                value = int(value)
                binary_code.extend(struct.pack(">B", (opcode << 5) | (reg & 0b11111)))
                binary_code.extend(struct.pack(">I", value))
                log_entries.append({"Opcode": opcode, "A": reg, "B": value})

            elif command == "WRITE_MEMORY":
                _, offset, base, source = parts
                offset = int(offset)
                base = int(base)
                source = int(source)
                binary_code.extend(struct.pack(">B", (opcode << 5) | (offset & 0b111)))
                binary_code.extend(struct.pack(">B", (base << 4) | (source & 0b1111)))
                log_entries.append({"Opcode": opcode, "Offset": offset, "Base": base, "Source": source})

            elif command == "UNARY_POPCNT":
                _, offset, base, dest = parts
                offset = int(offset)
                base = int(base)
                dest = int(dest)
                binary_code.extend(struct.pack(">B", (opcode << 5) | (offset & 0b111)))
                binary_code.extend(struct.pack(">B", (base << 4) | (dest & 0b1111)))
                log_entries.append({"Opcode": opcode, "Offset": offset, "Base": base, "Dest": dest})

    with open(output_file, "wb") as bin_file:
        bin_file.write(binary_code)

    with open(log_file, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["Opcode", "A", "B", "Offset", "Base", "Source", "Dest"])
        writer.writeheader()
        writer.writerows(log_entries)

def interpret(input_file, result_file, memory_range):
    with open(input_file, "rb") as bin_file:
        instructions = bin_file.read()

    pc = 0
    while pc < len(instructions):
        opcode = instructions[pc] >> 5
        if opcode == 4:
            reg = instructions[pc] & 0b11111
            value = struct.unpack(">I", instructions[pc + 1:pc + 5])[0]
            load_const(reg, value)
            pc += 5
        elif opcode == 6:
            offset = instructions[pc] & 0b111
            base = (instructions[pc + 1] >> 4) & 0b1111
            source = instructions[pc + 1] & 0b1111
            write_memory(offset, base, source)
            pc += 2
        elif opcode == 7:
            offset = instructions[pc] & 0b111
            base = (instructions[pc + 1] >> 4) & 0b1111
            dest = instructions[pc + 1] & 0b1111
            unary_popcnt(offset, base, dest)
            pc += 2

    start, end = map(int, memory_range.split('-'))
    with open(result_file, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Address", "Value"])
        for i in range(start, end + 1):
            writer.writerow([i, MEMORY[i]])

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "assemble":
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        log_file = sys.argv[4]
        assemble(input_file, output_file, log_file)
    elif mode == "interpret":
        input_file = sys.argv[2]
        result_file = sys.argv[3]
        memory_range = sys.argv[4]
        interpret(input_file, result_file, memory_range)
