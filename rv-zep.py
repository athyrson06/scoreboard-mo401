import numpy as np
import pandas as pd

# Define opcode constants
OPCODES = {
    'fld': 0,
    'fsd': 1,
    'fadd': 2,
    'fsub': 3,
    'fmul': 4,
    'fdiv': 5
}

# Define register prefix constants
REG_PREFIXES = {
    'x': 'int',
    'f': 'float'
}

def read_instruction_file(filename):
    instructions = []
    with open(filename, 'r') as f:
        for line in f:
            fields = line.strip().replace(',', ' ').split()
            
            opcode = fields[0].lower()


            if opcode not in OPCODES:
                raise ValueError(f'Invalid opcode: {opcode}')
            raw_instruction = line.replace('\n', '')
            opname = opcode
            opcode = OPCODES[opcode]

            rs1, rs2, rd, imm = 0, 0, 0, None  # Set imm to None by default
            rs1_type, rs2_type, rd_type = None, None, None
            # if opcode == 0:  # fld format: "instruction rd imm(rs1)"
            
            if opcode == 0:  # fld format: "instruction rd imm(rs1)"
                rd = int(fields[1][1:])
                rd_type = REG_PREFIXES[fields[1][0].lower()]
                rs1_imm = fields[2].split('(')
                imm = int(rs1_imm[0])
                rs1 = int(rs1_imm[1][1:-1])
                rs1_type = REG_PREFIXES[rs1_imm[1][0:1].lower()]


            # elif opcode == 1:  # fsd format: "instruction rs2 imm(rs1)"
            elif opcode == 1:
                rs2 = int(fields[1][1:])
                rs2_type = REG_PREFIXES[fields[1][0].lower()]
                rs1_imm = fields[2].split('(')
                imm = int(rs1_imm[0])
                rs1 = int(rs1_imm[1][1:-1])
                rs1_type = REG_PREFIXES[rs1_imm[1][0:1].lower()]


            else:  # Other instructions format: "instruction rd rs1 rs2"
                rd = int(fields[1][1:])
                rd_type = REG_PREFIXES[fields[1][0].lower()]
                rs1 = int(fields[2][1:])
                rs1_type = REG_PREFIXES[fields[2][0].lower()]
                if len(fields) > 3:
                    rs2 = int(fields[3][1:])
                    rs2_type = REG_PREFIXES[fields[3][0].lower()]
                else:
                    rs2 = 0
                    rs2_type = None


            instructions.append({
                'opcode': opcode,
                'rs1': rs1,
                'rs1_type': rs1_type,
                'rs2': rs2,
                'rs2_type': rs2_type,
                'rd': rd,
                'rd_type': rd_type,
                'imm': imm,
                'raw': raw_instruction,
                'opname' : opname,
            })
    return instructions

def explain_instruction(instruction):
    opcode = instruction['opcode']
    rs1 = instruction['rs1']
    rs2 = instruction['rs2']
    rd = instruction['rd']
    imm = instruction['imm']

    if opcode == 'fld':
        return f'{opcode} loads a value into register {rd} from the memory address {imm} + {rs1}'

    elif opcode == 'fsd':
        return f'{opcode} stores the value from register {rs2} into the memory address {imm} + {rs1}'

    else:
        if instruction['rs2_type'] is not None:
            if opcode == 'fadd':
                return f'{opcode} stores the result of register {rs1} + register {rs2} in register {rd}'
            elif opcode == 'fsub':
                return f'{opcode} stores the result of register {rs1} - register {rs2} in register {rd}'
            elif opcode == 'fmul':
                return f'{opcode} stores the result of register {rs1} * register {rs2} in register {rd}'
            elif opcode == 'fdiv':
                return f'{opcode} stores the result of register {rs1} / register {rs2} in register {rd}'
        else:
            return f'{opcode} stores the result of register {rs1} in  register {rd}'

# def read_instruction(instruction):
#     print(instruction)
#     opcode = instruction['opcode']
#     rs1 = instruction['rs1']
#     rs2 = instruction['rs2']
#     rd = instruction['rd']
#     imm = instruction['imm']

#     return opcode, rs1, rs2, rd, imm

# # Example usage
# _, instructions = read_instruction_file('example.s')

def read_configs(filename):
    configs = {}
    with open(filename, 'r') as f:
        for line in f:
            fields = line.strip().split()
            unidade = fields[0].lower()
            n_unidades = int(fields[1])
            n_ciclos = int(fields[2])
            configs[unidade] = {
                'n_unidades': n_unidades,
                'n_ciclos': n_ciclos
            }
        # configs['fld'] = {
        #         'n_unidades': configs['int']['n_unidades'],
        #         'n_ciclos': configs['int']['n_ciclos']
        #     }
        # configs['fsd'] = {
        #         'n_unidades': configs['int']['n_unidades'],
        #         'n_ciclos': configs['int']['n_ciclos']
        #     }
        # configs['sub'] = {
        #         'n_unidades': configs['add']['n_unidades'],
        #         'n_ciclos': configs['add']['n_ciclos']
        #     }
    return configs

configs = read_configs('conf.s')
instructions = read_instruction_file('example.s')

def ignore():
    # data = {
    #     'Instruction': [i for i in instructions],
    #     'Issue': [0 for idx, _ in enumerate(instructions)],
    #     'Read' : [0 for idx_, _ in enumerate(instructions)],
    #     'Execute' : [0 for idx_idx, _ in enumerate(instructions)],
    #     'Write' : [0 for idx_idx, _ in enumerate(instructions)],
    # }

    # scoreboarding = pd.DataFrame(data)
    # # print(scoreboarding)

    # cicle = 0
    # def score_nick(n):
    #     return scoreboarding.loc[scoreboarding.index == n, :]

    # def manual_update_score(inst_number, issue=0, read=0, execute=0, write=0):
    #     current_inst = score_nick(inst_number)
    #     # print(current_inst)
    #     return current_inst

    # print(manual_update_score(3))

    # for cicle in range(1,100):
    #     if cicle > 3:
    #         scoreboarding.iloc[-1,-1] = 1
    #     print(score_nick(1))
    #     if scoreboarding.iloc[-1,-1] == 1:
    #         break
    # # for i in instructions: 
    #     print(i)
        # print(read_instruction(i))
        # break
    pass

class ScoreBoarding:
    def __init__(self, configs = {}):
        # Initial empty DataFrame setup
        self.columns = ['Instruction', 'Issue', 'Read', 'Execute', 'Write']
        self.scoreboarding = pd.DataFrame(columns=self.columns)
        self.base_inst = {
            'Instruction': '',
            'Issue': False,
            'Read': False,
            'Execute': False,
            'Write': False,
            'type': '',
            'n_ciclos': 1,
        }
        self.n_insts = 0
        self.n_cols = 5
        self.inst_order = []
        self.current_cicle = 0
        self.configs = configs
        self.cicle_usage = [0, ]

    def get_unit(self, inst_type):
        if inst_type == 'fld' or inst_type == 'fsd':
            return 'int'
        elif inst_type == 'fadd' or inst_type == 'fsub':
            return 'add'
        elif inst_type == 'fmul':
            return 'mult'
        elif inst_type == 'fdiv':
            return 'div'

    def add_instruction(self, inst):
        # Create a copy of the base instruction
        new_inst = self.base_inst.copy()
        # Update the 'Instruction' field with the provided inst value
        new_inst['Instruction'] = inst['raw']
        new_inst['type'] = inst['opname']
        # Check if the instruction is in the configs dictionary
        inst_unit = self.get_unit(inst['opname'])
        new_inst['n_ciclos'] = int(self.configs[inst_unit]['n_ciclos'])
        inst_df = pd.DataFrame([new_inst])
        inst_df['n_ciclos'] =inst_df['n_ciclos'].astype('Int64')
        # Append the new instruction to the DataFrame
        self.scoreboarding = pd.concat([self.scoreboarding, inst_df],
                             ignore_index=True)

        index_inst = self.scoreboarding.index[-1]
        self.n_insts = self.scoreboarding.index[-1] + 1
        

    def update_instruction_1(self, inst_number):
        current_inst = self.scoreboarding.loc[self.scoreboarding.index == inst_number, :]
        n_ciclos = int(current_inst['n_ciclos'].values[0])

        for idc in range(1, self.n_cols):
            if idc != 3:
                if current_inst.iloc[ 0, idc] == False:
                    self.current_cicle += 1
                    self.scoreboarding.iloc[
                        self.scoreboarding.index == inst_number, idc
                                        ] = self.current_cicle
                    break
            else:
                if current_inst.iloc[ 0, idc] == False:
                    self.current_cicle += n_ciclos
                    self.scoreboarding.iloc[
                        self.scoreboarding.index == inst_number, idc
                                        ] = self.current_cicle

                    break

    def update_instruction(self, inst_number):
        current_inst = self.scoreboarding.loc[self.scoreboarding.index == inst_number, :]
        n_ciclos = int(current_inst['n_ciclos'].values[0])

        for idc in range(1, self.n_cols):
            if idc != 3:
                if current_inst.iloc[ 0, idc] == False:
                    self.current_cicle += 1
                    self.scoreboarding.iloc[
                        self.scoreboarding.index == inst_number, idc
                                        ] = self.current_cicle
                    break
            else:
                if current_inst.iloc[ 0, idc] == False:
                    self.current_cicle += n_ciclos
                    self.scoreboarding.iloc[
                        self.scoreboarding.index == inst_number, idc
                                        ] = self.current_cicle

                    break

    def __str__(self):
        return self.scoreboarding.to_string()

# for c in configs.items():
#     print(c)

# Example usage
sb = ScoreBoarding(configs=configs)


for i in instructions:
    sb.add_instruction(i)


# sb.main()

sb.update_instruction(0)
sb.update_instruction(0)
sb.update_instruction(0)
sb.update_instruction(1)

print(sb)

# # def split_into_chunks(lst, chunk_size=4):
# #     return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


# # flat_list = sum(sb.inst_order, [])
# # s = sorted(flat_list, key=lambda x: x[1])
# # print(s)

# # for i in split_into_chunks(s):
# #     print(i)
# # # for i in sb.inst_order:
# # #     print(i)

# c = read_configs('conf.s')
# for i in c:
#     print(i)