import sys
input_file_name_of_sys= sys.argv[1]


out_put_dile_name = sys.argv[2]


out_put_dile_name_R = sys.argv[3] 


Register_value={"00000":0, "00001":0, "00010":380, "00011":0, "00100":0, "00101":0, "00110":0, "00111":0,"01000":0, "01001":0, "01010":0, "01011":0, "01100":0, "01101":0, "01110":0, "01111":0,"10000":0, "10001":0, "10010":0, "10011":0, "10100":0, "10101":0, "10110":0, "10111":0,"11000":0, "11001":0, "11010":0, "11011":0, "11100":0, "11101":0, "11110":0, "11111":0}
g=open(out_put_dile_name_R,"w")


g_b=open(out_put_dile_name,"w")

PC_VALUE=0

def twos_complement(bin_str):
    bin_str = list(bin_str)
    for i in range(len(bin_str)):
        bin_str[i] = '1' if bin_str[i] == '0' else '0'
    bin_str = ''.join(bin_str)
    bin_str = bin(int(bin_str, 2) + 1)
    return bin_str[2:] 
  
def ddecii_to_hexaaa(decimal_num):
    return "0x" + format(decimal_num, "08X")

def decimal_to_binary1(number, bits):
    if number > 0:
        return bin(number)[2:].zfill(bits)
    elif number < 0:
        return twos_complement(bin(-number)[2:].zfill(bits))
    else:
        return "0" * bits
    
def decimal_to_binary(number, bits):
    if number >= 0:
        binary = bin(number)[2:]
        if len(binary) < bits:
            binary = binary.zfill(bits)
        return binary
    else:
        binary = bin((1 << bits) + number)[2:]
        if len(binary) < bits:
            binary = binary.zfill(bits)
        return binary



def binary_to_decimal(binary):
    if binary[0] == '1':
        positive_binary = twos_complement(binary)
        return -int(positive_binary, 2)
    else:
        return int(binary, 2)
    
Memory = {65536: 0,65540: 0,65544: 0,65548: 0,65552: 0,65556: 0,65560: 0,65564: 0,65568: 0,65572: 0,65576: 0,65580: 0,65584: 0,65588: 0,65592: 0,65596: 0,65600: 0,65604: 0,65608: 0,65612: 0,65616: 0,65620: 0,65624: 0,65628: 0,65632: 0,65636: 0,65640: 0,65644: 0,65648: 0,65652: 0,65656: 0,65660: 0}
R_type={"00000000000110011":"ADD","00000001010110011":"SRL","00000000100110011":"SLT","01000000000110011":"SUB","00000001100110011":"OR","00000001110110011":"AND"}
I_type={"0100000011":"LW","0000010011":"ADDI","0001100111":"JALR"}
S_type={"0000100011":"SW"}
B_type={"0001100011":"BEQ","0011100011":"BNE","1001100011":"BLT"}   
J_type={"1101111":"JAL"}
opcode_define={"0110011":"R","0000011":"I","0010011":"I","1100111":"I","1100011":"B","1101111":"J","0100011":"S","0101010":"RVRS","0000000":"RST","1111111":"MUL","1100110":"HALT"}
def R_instruction(instruction):
    x=instruction[0:7]+instruction[17:20]+instruction[25:32]
    instruction_tyope=R_type.get(x)
    rs1=instruction[12:17]
    rs2=instruction[7:12]
    rd=instruction[20:25]     #Apply if conditio
    if rd=="00000":
        return
    else:
        if instruction_tyope=="ADD":
            x=Register_value[rs1]+Register_value[rs2]
            Register_value[rd]=x
            return
        elif instruction_tyope=="SUB":
            x=Register_value[rs1]-Register_value[rs2]
            Register_value[rd]=x
            return
        elif instruction_tyope == "SRL":
            y = decimal_to_binary(Register_value[rs2], 32)
            y = binary_to_decimal(y[27:32])  
            x = Register_value[rs1] >> y  
            Register_value[rd] = x
            return
        elif instruction_tyope=="SLT":
            x=Register_value[rs1]
            y=Register_value[rs2]
            if x<y:
                Register_value[rd]=1
            return
        elif instruction_tyope=="AND":
           x = ["0"] * 32
           rs1_bin = decimal_to_binary(Register_value[rs1], 32)
           rs2_bin = decimal_to_binary(Register_value[rs2], 32)
           for i in range(32):
                 if rs1_bin[i] == "1" and rs2_bin[i] == "1":
                    x[i] = "1"
           x = "".join(x)  
           Register_value[rd] = binary_to_decimal(x)
           return
        elif instruction_tyope=="OR":
            x=["0"]*32
            rs1_binary=decimal_to_binary(Register_value[rs1],32)
           
            rs2_binary=decimal_to_binary(Register_value[rs2],32)
           
            for i in range(32):
                if rs1_binary[i]=="1" or rs2_binary[i]=="1":
                    x[i]="1"
            x="".join(x)
          
            Register_value[rd]=binary_to_decimal(x)
        
            return
    return 

def I_instruction(instruction,PC_VALUE):
    instruction_tyope=I_type.get(instruction[17:20] + instruction[25:32])
    rs1=instruction[12:17]
    rd=instruction[20:25]
    immediate_adding_value=instruction[0:12]
    if instruction_tyope=="ADDI":
        immediate_adding_value=binary_to_decimal(immediate_adding_value)
        temp=immediate_adding_value + Register_value.get(rs1)
        if rd=="00000":
            return
        else:
           Register_value[rd]=temp
    elif instruction_tyope=="LW":
      if rd=="00000":
          return
      else:
        memory_address_adding=int(Register_value.get(rs1) + binary_to_decimal(immediate_adding_value))
        if memory_address_adding  in Memory:
            Register_value[rd]=Memory.get(memory_address_adding)
            return
        else:
            Memory[memory_address_adding]=0
            Register_value[rd]=Memory.get(memory_address_adding)
            return
            
    elif instruction_tyope=="JALR":
        if rd=="00000":
            PC_VALUE=Register_value.get(rs1) + binary_to_decimal(immediate_adding_value)
            return PC_VALUE
        else:
          
            Register_value[rd]=PC_VALUE+4;
            PC_VALUE=Register_value.get(rs1) + binary_to_decimal(immediate_adding_value)
           
            return PC_VALUE
    
def B_instruction(instruction,PC_VALUE):
    instruction_tyope = B_type.get(instruction[17:20] + instruction[25:32])
    value_of_rs1 = Register_value.get(instruction[12:17])
    value_of_rs2 = Register_value.get(instruction[7:12])
    immediate_adding_value = instruction[0] + instruction[24] + instruction[1:7] + instruction[20:24]
    immediate_adding_value = binary_to_decimal(immediate_adding_value)
    immediate_adding_value = immediate_adding_value * 2 

    if instruction_tyope == "BEQ":
        if value_of_rs1 == value_of_rs2:
            PC_VALUE = PC_VALUE + immediate_adding_value 

            return str(PC_VALUE)
        else:
     
            p=str(PC_VALUE+4)
            return p
    elif instruction_tyope == "BNE":
        if value_of_rs1 != value_of_rs2:
            PC_VALUE = PC_VALUE + immediate_adding_value
       
            p=str(PC_VALUE)
            return p
        else:
          
            p=str(PC_VALUE+4)
            return p
    elif instruction_tyope == "BLT":
        if value_of_rs1 < value_of_rs2:
            PC_VALUE = PC_VALUE + immediate_adding_value
         
            p=str(PC_VALUE)
            return p
        else:
         
            p=str(PC_VALUE+4)
            return p



def J_instruction(instruction,PC_VALUE):
    immediate_adding_value = instruction[0] + instruction[12:20] + instruction[11] + instruction[1:11] + "0"
    immediate_adding_value=binary_to_decimal(immediate_adding_value)
    rd=instruction[20:25]
    if rd=="00000":
        return PC_VALUE+4
    else:
       Register_value[rd]=PC_VALUE + 4 
       PC_VALUE=PC_VALUE+immediate_adding_value
       return PC_VALUE
   
def S_instruction(instruction):
    rs2=instruction[7:12]
    rs1=instruction[12:17]
    immediate_adding_value=instruction[0:7]+instruction[20:25]
    immediate_adding_value=binary_to_decimal(immediate_adding_value)
    rs1_value=Register_value.get(rs1)
    memory_address_addingress=rs1_value+immediate_adding_value
  
    Memory[memory_address_addingress]=Register_value.get(rs2)
   
    return  

   
def print_values():
    for i in (Register_value.values()):
      
        a="0b"+decimal_to_binary(i,32)
        a=" "+a
        i=" "+str(i)
        g_b.write(a)
        g.write(i)

    g.write(" "+'\n')
    g_b.write(" "+'\n')
    return


data_in_list=[]
f=open(input_file_name_of_sys,"r")
for line in f.readlines():
    if len(line.strip())>0:
        data_in_list.append(line.strip())

i=0

while(i<len(data_in_list)):
  
    oPC_VALUEode=data_in_list[i][25:32]
    instruction_type=opcode_define[oPC_VALUEode]
    if instruction_type=="R":
        R_instruction(data_in_list[i])
        i=i+1
        PC_VALUE=(i)*4
        P="0b"+decimal_to_binary(PC_VALUE,32)
        tem=str(PC_VALUE)
        g.write(tem)
        g_b.write(P)
        
        print_values()
    elif instruction_type=="B":
        if data_in_list[i]=="00000000000000000000000001100011":
            PC_VALUE=i*4
            P="0b"+decimal_to_binary(PC_VALUE,32)
            tem=str(PC_VALUE)
            g.write(tem)
            g_b.write(P)
           
            print_values()
            i=i+4
            break;
        b=int(B_instruction(data_in_list[i],PC_VALUE))
        PC_VALUE=b
   
       
        P="0b"+decimal_to_binary(PC_VALUE,32)
        g.write(str(PC_VALUE))
        g_b.write(P)
        i=int(PC_VALUE/4) 
       
        print_values()
        
    elif instruction_type=="S":
        S_instruction(data_in_list[i])
        i=i+1
        PC_VALUE=i*4
        P="0b"+decimal_to_binary(PC_VALUE,32)
        tem=str(PC_VALUE)
       
        g_b.write(P)
        g.write(tem)
        print_values()
    elif instruction_type=="I":
        if oPC_VALUEode=="1100111":
                    PC_VALUE=I_instruction(data_in_list[i],PC_VALUE)
                  
                    i=int(PC_VALUE//4)
                    tem=str(PC_VALUE)
                    P="0b"+decimal_to_binary(PC_VALUE,32)
                    g_b.write(P)
                  
                    g.write(tem)
                    print_values()
                    
        else:
                    I_instruction(data_in_list[i],PC_VALUE)
                    i=i+1
                    PC_VALUE=i*4
                    P="0b"+decimal_to_binary(PC_VALUE,32)
                    tem=str(PC_VALUE)
                 
                    g_b.write(P)
                    g.write(tem)
                    print_values()
    elif instruction_type=="J":
        PC_VALUE=J_instruction(data_in_list[i],PC_VALUE)
        i=PC_VALUE//4
        tem=str(PC_VALUE)
        P="0b"+decimal_to_binary(PC_VALUE,32)
        g_b.write(P)
        #print(tem)
        g.write(tem)
        print_values()

    elif instruction_type=="MUL":
            x=Register_value.get(data_in_list[i][12:17])*Register_value.get(data_in_list[i][7:12])
            Register_value[data_in_list[i][20:25]]=x
            i=i+1
            PC_VALUE=(i)*4
            P="0b"+decimal_to_binary(PC_VALUE,32)
            tem=str(PC_VALUE)
            g.write(tem)
            g_b.write(P)
              
            print_values()
    elif instruction_type=="HALT":
        tem=str(PC_VALUE)
        P="0b"+decimal_to_binary(PC_VALUE,32)
        g_b.write(P)
      
        g.write(tem)
        print_values()
        break
        
    else:
       
        g.write("INVALID ")
        g.write("Instruction")
        g_b.write("INVALID ")
        g_b.write("Instruction")
        tem=str(PC_VALUE)
        i=i+1
        PC_VALUE=i*4
        break

for j in (Memory.keys()):
    
    a=str(ddecii_to_hexaaa(j))+":"+"0b"+decimal_to_binary((Memory[j]),32)
    if j==65660:
        b=ddecii_to_hexaaa(j)+":"+str(Memory[j])
        g.write(b)
        g_b.write(a)
        break;
    else:
        a=a+"\n"
        g_b.write(a)
        b=ddecii_to_hexaaa(j)+":"+str(Memory[j])+"\n"
        g.write(b)