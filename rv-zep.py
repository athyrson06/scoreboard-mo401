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

configs = pd.DataFrame(read_configs('conf.s'))

instructions = read_instruction_file('example.s')

class ScoreBoard:
    def __init__(self, configs = {}):
        # Initial empty DataFrame setup
        self.columns = ['Instruction', 'Issue', 'Read', 'Execute', 'Write']
        self.scoreboard = pd.DataFrame(columns=self.columns)
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
        self.registers = pd.DataFrame({
            'int': ['-' for i in range(32)],
            'float': ['-' for i in range(32)]
        })


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
        inst_df['n_ciclos'] = inst_df['n_ciclos'].astype('Int64')
        # Append the new instruction to the DataFrame
        self.scoreboard = pd.concat([self.scoreboard, inst_df],
                             ignore_index=True)

        index_inst = self.scoreboard.index[-1]
        self.n_insts = self.scoreboard.index[-1] + 1
        self.inst_order.append([i for i in range(index_inst + 1,index_inst + 5)])
        

    def update_instruction_1(self, inst_number):
        current_inst = self.scoreboard.loc[self.scoreboard.index == inst_number, :]
        n_ciclos = int(current_inst['n_ciclos'].values[0])

        for idc in range(1, self.n_cols):
            if idc != 3:
                if current_inst.iloc[ 0, idc] == False:
                    self.current_cicle += 1
                    self.scoreboard.iloc[
                        self.scoreboard.index == inst_number, idc
                                        ] = self.current_cicle
                    break
            else:
                if current_inst.iloc[ 0, idc] == False:
                    self.current_cicle += n_ciclos
                    self.scoreboard.iloc[
                        self.scoreboard.index == inst_number, idc
                                        ] = self.current_cicle

                    break

    def update_instruction(self, inst_number):
        current_inst = self.scoreboard.loc[self.scoreboard.index == inst_number, :]
        n_ciclos = int(current_inst['n_ciclos'].values[0])

        for idc in range(1, self.n_cols):
            if idc != 3:
                if current_inst.iloc[ 0, idc] is False:
                    self.current_cicle += 1
                    self.scoreboard.iloc[
                        self.scoreboard.index == inst_number, idc
                                        ] = self.current_cicle
                    break
            else:
                if current_inst.iloc[ 0, idc] is False:
                    self.current_cicle += n_ciclos
                    self.scoreboard.iloc[
                        self.scoreboard.index == inst_number, idc
                                        ] = self.current_cicle

                    break

    def __str__(self):
        return self.scoreboard.to_string()

    def update_scoreboard(self):
        for inst in range(len(self.inst_order)):
            print(self.inst_order[inst])
            for cicle in range(4):
                
                self.update_instruction(inst)


class FunctionalUnit():
    OPTOUNIT = {
            'fld': 'int',
            'fsd': 'int',
            'fadd': 'add',
            'fsub': 'add',
            'fmul': 'mult',
            'fdiv': 'div'
        }

    def __init__(self, config):
        self.base_status = {
            'unit': '',
            'busy': False,
            'op': None,
            'fi': None,
            'fj': None,
            'fk': None,
            'qj': None,
            'qk': None,
            'rj': None,
            'rk': None,
            'cicles_left': 0,
        }
        self.config = config
        self.functionalunit = pd.DataFrame(columns=self.base_status.keys())
        self.fill_unit()
        

    def fill_unit(self):
        for c in self.config.columns:
            new_unit = self.base_status.copy()
            for unit in range(self.config.loc['n_unidades', c]):
                new_unit['unit'] = f'{c}_{unit+1}'
                unit_df = pd.DataFrame([new_unit])
                self.functionalunit = pd.concat([self.functionalunit, unit_df],
                             ignore_index=True)


    
    def start_unit(self, op, fi, fj, fk = None, qj = None, qk = None):
        unit_type = self.OPTOUNIT[op]
        unit = False
        for u in self.functionalunit['unit']:
            if (u[:-2] == unit_type) and (
                self.functionalunit.loc[
                    self.functionalunit['unit'] == u, 'busy'].values[0] == False):
                unit = u
                break
        if not unit:
            print(f'cannot start {op}')
            return False
        print('can')
        self.functionalunit.loc[self.functionalunit['unit'] == unit, 'busy'] = True
        self.functionalunit.loc[self.functionalunit['unit'] == unit, 'op'] = op
        self.functionalunit.loc[self.functionalunit['unit'] == unit, 'fi'] = fi
        self.functionalunit.loc[self.functionalunit['unit'] == unit, 'fj'] = fj
        self.functionalunit.loc[self.functionalunit['unit'] == unit, 'fk'] = fk
        self.functionalunit.loc[self.functionalunit['unit'] == unit, 'qj'] = qj
        self.functionalunit.loc[self.functionalunit['unit'] == unit, 'qk'] = qk
        self.functionalunit.loc[self.functionalunit['unit'] == unit, 'rj'] = False
        self.functionalunit.loc[self.functionalunit['unit'] == unit, 'rk'] = False
        self.functionalunit.loc[self.functionalunit['unit'] == unit, 'cicles_left'] = self.config.loc['n_ciclos', unit_type]
        
        return True

print(configs)

# Example usage
sb = ScoreBoard(configs=configs)


for i in instructions:
    sb.add_instruction(i)


# sb.main()

sb.update_scoreboard()


# print(sb.inst_order)
print(sb.scoreboard)


fu = FunctionalUnit(configs)

for i in instructions:
    fu.start_unit(i['opname'], i['rd'], i['rs1'], i['rs2'])

print(fu.functionalunit)

