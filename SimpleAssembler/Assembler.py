import sys
INSTR_ENCODING = {
    
    "add":  {
        "opcode": "0110011",
        "funct3": "000",
        "funct7": "0000000",
    },
    "sub":  {
        "opcode": "0110011",
        "funct3": "000",
        "funct7": "0100000",
    },
    "slt":  {
        "opcode": "0110011",
        "funct3": "010",
        "funct7": "0000000",
    },
    "srl":  {
        "opcode": "0110011",
        "funct3": "101",
        "funct7": "0000000",
    },
    "or":   {
        "opcode": "0110011",
        "funct3": "110",
        "funct7": "0000000",
    },
    "and":  {
        "opcode": "0110011",
        "funct3": "111",
        "funct7": "0000000",
    },
    "lw": {
        "opcode": "0000011",
        "funct3": "010",
    },
    
    "addi": {
        "opcode": "0010011",
        "funct3": "000",
    },
    "jalr": {
        "opcode": "1100111",
        "funct3": "000",
    },

    "sw": {
        "opcode": "0100011",
        "funct3": "010",
    },
    "beq": {
        "opcode": "1100011",
        "funct3": "000",
    },
    "bne": {
        "opcode": "1100011",
        "funct3": "001",
    },

    "blt": {
        "opcode": "1100011",
        "funct3": "100",
    },

    "jal": {
        "opcode": "1101111",
    },
}
REGISTER_MAP = {
    "zero": "00000",  
    "ra":   "00001",  
    "sp":   "00010",  
    "gp":   "00011", 
    "tp":   "00100",  
    "t0":   "00101",  
    "t1":   "00110",  
    "t2":   "00111",  
    "s0":   "01000", 
    "fp":   "01000",  
    "s1":   "01001",  
    "a0":   "01010",  
    "a1":   "01011",  
    "a2":   "01100",  
    "a3":   "01101",  
    "a4":   "01110",  
    "a5":   "01111",  
    "a6":   "10000",  
    "a7":   "10001",  
    "s2":   "10010",  
    "s3":   "10011",  
    "s4":   "10100",  
    "s5":   "10101",  
    "s6":   "10110",  
    "s7":   "10111",  
    "s8":   "11000",  
    "s9":   "11001",  
    "s10":  "11010",  
    "s11":  "11011",  
    "t3":   "11100",  
    "t4":   "11101", 
    "t5":   "11110", 
    "t6":   "11111",  
}

def to_signed_imm(value, bits):
    min_val = -(1 << (bits - 1))
    max_val = (1 << (bits - 1)) - 1
    if value < min_val or value > max_val:
        raise ValueError(f"Immediate {value} out of range for {bits}-bit signed field.")
    if value < 0:
        value = (1 << bits) + value
    return format(value, f'0{bits}b')

def parse_register(reg_str, line_num):
    if reg_str not in REGISTER_MAP:
        raise ValueError(f"Line {line_num}: Invalid register name '{reg_str}'.")
    return REGISTER_MAP[reg_str]

def first_pass_collect_labels(lines):
    label_map = {}
    pc = 0

    for i, line in enumerate(lines):
        text = line.strip()
        if not text:
            continue
        if ":" in text:
            possible_label = text.split(":")[0].strip()
            if possible_label.isalpha() or possible_label.replace("_", "").isalnum():
                
                label_map[possible_label] = pc
                
        after_label_part = ""
        if ":" in text:
            parts = text.split(":", maxsplit=1)
            after_label_part = parts[1].strip()
        else:
            after_label_part = text

        if after_label_part: 
            pc += 4  
    
    return label_map
def translate_instructions_to_binary(lines, label_map):
   
    pc = 0
    output_binary = []
    last_instruction_addr = None

    for line_num, orig_line in enumerate(lines, start=1):
        text = orig_line.strip()
        if not text:
            continue
        label_part = ""
        instr_part = text
        if ":" in text:
            label_split = text.split(":", maxsplit=1)
            label_part = label_split[0].strip()
            if len(label_split) > 1:
                instr_part = label_split[1].strip()
            else:
                instr_part = ""  
        if not instr_part:
            continue
        tokens = instr_part.replace(",", " ").split()
        mnemo = tokens[0] 
        operands = tokens[1:] 
        if mnemo == "beq" and len(operands) == 3:
            if operands[0] == "zero" and operands[1] == "zero":
                try:
                    imm_val = int(operands[2], 0) 
                    if imm_val == 0:
                        last_instruction_addr = pc
                except:
                    pass
        if mnemo not in INSTR_ENCODING:
            raise ValueError(f"Line {line_num}: Unrecognized instruction '{mnemo}'.")
        inst_bin = encode_instruction(mnemo, operands, pc, label_map, line_num)
        output_binary.append(inst_bin)
        
        pc += 4 
    if last_instruction_addr is None:
        raise ValueError("Missing Virtual Halt instruction (beq zero, zero, 0).")
    if last_instruction_addr != (pc - 4):
        raise ValueError("Virtual Halt is not the last instruction in the file.")

    return output_binary
def encode_instruction(mnemo, operands, pc, label_map, line_num):
    info = INSTR_ENCODING[mnemo]
    opcode = info["opcode"]
    if opcode == "0110011":
        if len(operands) != 3:
            raise ValueError(f"Line {line_num}: R-type instruction '{mnemo}' requires 3 operands.")
        rd_str, rs1_str, rs2_str = operands
        rd_bin  = parse_register(rd_str, line_num)
        rs1_bin = parse_register(rs1_str, line_num)
        rs2_bin = parse_register(rs2_str, line_num)
        funct3 = info["funct3"]
        funct7 = info["funct7"]
        return funct7 + rs2_bin + rs1_bin + funct3 + rd_bin + opcode
    elif opcode in ["0000011", "0010011", "1100111"]:
        if mnemo == "lw" or mnemo == "sw":
            pass
        if mnemo == "lw":
            if len(operands) != 2:
                raise ValueError(f"Line {line_num}: lw must have 2 operands: lw rd, imm(rs1)")
            rd_str, rest = operands
            rd_bin = parse_register(rd_str, line_num)
            imm_val, rs1_name = parse_mem_operand(rest, line_num)  
            rs1_bin = parse_register(rs1_name, line_num)
            imm_bin = to_signed_imm(imm_val, 12)
            funct3 = info["funct3"]
            return imm_bin + rs1_bin + funct3 + rd_bin + opcode

        elif mnemo == "addi":
            if len(operands) != 3:
                raise ValueError(f"Line {line_num}: addi must have 3 operands.")
            rd_str, rs1_str, imm_str = operands
            rd_bin  = parse_register(rd_str, line_num)
            rs1_bin = parse_register(rs1_str, line_num)
            imm_val = int(imm_str, 0) 
            imm_bin = to_signed_imm(imm_val, 12)
            funct3 = info["funct3"]  
            return imm_bin + rs1_bin + funct3 + rd_bin + opcode

        elif mnemo == "jalr":
            if len(operands) != 3:
                raise ValueError(f"Line {line_num}: jalr must have 3 operands.")
            rd_str, rs1_str, imm_str = operands
            rd_bin = parse_register(rd_str, line_num)
            rs1_bin = parse_register(rs1_str, line_num)
            print(imm_str)
            imm_val = int(imm_str, 10)
            imm_bin = to_signed_imm(imm_val, 12)
            funct3 = info["funct3"]  
            return imm_bin + rs1_bin + funct3 + rd_bin + opcode
    elif opcode == "0100011":
        if mnemo == "sw":
            if len(operands) != 2:
                raise ValueError(f"Line {line_num}: sw must have 2 operands.")
            rs2_str, rest = operands
            rs2_bin = parse_register(rs2_str, line_num)
            imm_val, rs1_name = parse_mem_operand(rest, line_num)
            rs1_bin = parse_register(rs1_name, line_num)
            imm_bin = to_signed_imm(imm_val, 12)  

            funct3 = info["funct3"] 
            imm_high_7 = imm_bin[0:7]
            imm_low_5  = imm_bin[7:12]
            return imm_high_7 + rs2_bin + rs1_bin + funct3 + imm_low_5 + opcode
    elif opcode == "1100011":
        if len(operands) != 3:
            raise ValueError(f"Line {line_num}: B-type '{mnemo}' requires 3 operands (rs1, rs2, label/immediate).")

        rs1_str, rs2_str, label_or_imm = operands
        rs1_bin = parse_register(rs1_str, line_num)
        rs2_bin = parse_register(rs2_str, line_num)
        funct3 = info["funct3"]
        if label_or_imm in label_map:
            target_addr = label_map[label_or_imm]
            offset_bytes = target_addr - (pc) 
        else:
            try:
                offset_bytes = int(label_or_imm, 0)
            except:
                raise ValueError(f"Line {line_num}: Unknown label/immediate '{label_or_imm}'.")
        offset_halfwords = offset_bytes >> 1
        if (offset_bytes % 2) != 0:
            raise ValueError(f"Line {line_num}: Branch to an odd offset not aligned by 2? offset={offset_bytes}")

        imm_bin = to_signed_imm(offset_halfwords, 12)
        bit_11   = imm_bin[1]  
        bits_10_5= imm_bin[2:8]
        bits_4_1 = imm_bin[8:12]
        bit_12   = imm_bin[0]
        return bit_12 + bits_10_5 + rs2_bin + rs1_bin + funct3 + bits_4_1 + bit_11 + opcode
    elif opcode == "1101111":
        if len(operands) != 2:
            raise ValueError(f"Line {line_num}: J-type 'jal' requires 2 operands: jal rd, label/immediate.")

        rd_str, label_or_imm = operands
        rd_bin = parse_register(rd_str, line_num)
        
        if label_or_imm in label_map:
            target_addr = label_map[label_or_imm]
            offset_bytes = target_addr - pc
        else:
            try:
                offset_bytes = int(label_or_imm, 0)
            except:
                raise ValueError(f"Line {line_num}: Unknown label/immediate '{label_or_imm}' for jal.")
        offset_halfwords = offset_bytes >> 1
        if (offset_bytes % 2) != 0:
            raise ValueError(f"Line {line_num}: jal offset is not halfword aligned => {offset_bytes}")
        imm_bin = to_signed_imm(offset_halfwords, 20)
        imm_bin = imm_bin[::-1]
        bit_20   = imm_bin[19]
        bits_10_1= imm_bin[9:19]
        bit_11   = imm_bin[8]
        bits_19_12 = imm_bin[0:8]


        return (bit_20 + bits_10_1 + bit_11 + bits_19_12 + rd_bin + opcode)
    else:
        raise ValueError(f"Line {line_num}: Unhandled instruction '{mnemo}'.")

def parse_mem_operand(mem_str, line_num):
    if "(" not in mem_str or ")" not in mem_str:
        raise ValueError(f"Line {line_num}: invalid memory operand '{mem_str}'. Must be imm(reg).")
    before_paren, after_paren = mem_str.split("(", maxsplit=1)
    imm_str = before_paren.strip()
    after_paren = after_paren.strip()
    if not after_paren.endswith(")"):
        raise ValueError(f"Line {line_num}: invalid memory operand '{mem_str}'. Missing closing paren.")
    reg_name = after_paren[:-1].strip()  

    imm_val = int(imm_str, 0)
    return (imm_val, reg_name)

def assemble_file(input_file, output_file):
    with open(input_file, "r") as f:
        lines = f.readlines()
    try:
        label_map = first_pass_collect_labels(lines)
        binary_lines = translate_instructions_to_binary(lines, label_map)
        with open(output_file, "w") as outf:
            for i, bline in enumerate(binary_lines):
                if i < len(binary_lines) - 1:
                    outf.write(bline + "\n")
                else:
                    outf.write(bline)  
        
    except ValueError as e:
        print(f"Assembler Error: {e}")
        sys.exit(1)
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:  python3 assembler.py  <input_asm_file>  <output_bin_file>")
        sys.exit(1)
    input_asm = sys.argv[1]
    output_bin = sys.argv[2]
    assemble_file(input_asm, output_bin)
    print("Assembly complete. No errors found.")