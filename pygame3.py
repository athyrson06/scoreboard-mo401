import pygame
import sys

# Define opcode constants
OPCODES = {
    'fld': 'fld',
    'fsd': 'fsd',
    'fadd': 'fadd',
    'fsub': 'fsub',
    'fmul': 'fmul',
    'fdiv': 'fdiv'
}

# Define register prefix constants
REG_PREFIXES = {
    'x': 'int',
    'f': 'float'
}

def parse_file(filename):
    instructions = []
    with open(filename, 'r') as f:
        for line in f:
            fields = line.strip().replace(',', ' ').split()
            opcode = fields[0].lower()
            if opcode not in OPCODES:
                raise ValueError(f'Invalid opcode: {opcode}')

            opcode = OPCODES[opcode]

            rs1, rs2, rd, imm = 0, 0, 0, None  # Set imm to None by default
            rs1_type, rs2_type, rd_type = None, None, None
            
            if opcode == 'fld':  # fld format: "instruction rd imm(rs1)"
                rd = int(fields[1][1:])
                rd_type = REG_PREFIXES[fields[1][0].lower()]
                rs1_imm = fields[2].split('(')
                imm = int(rs1_imm[0])
                rs1 = int(rs1_imm[1][1:-1])
                rs1_type = REG_PREFIXES[rs1_imm[1][0:1].lower()]

            elif opcode == 'fsd':
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
                'imm': imm
            })
    return instructions

def read_instruction(instruction):
    opcode = instruction['opcode']
    rs1 = instruction['rs1']
    rs2 = instruction['rs2']
    rd = instruction['rd']
    imm = instruction['imm']

    if opcode == 'fld':
        return f'({opcode}) loads a value into register {rd} from the memory address {imm} + {rs1}'
    elif opcode == 'fsd':
        return f'({opcode}) stores the value from register {rs2} into the memory address {imm} + {rs1}'
    else:
        if instruction['rs2_type'] is not None:
            if opcode == 'fadd':
                return f'({opcode}) stores the result of register {rs1} + register {rs2} in register {rd}'
            elif opcode == 'fsub':
                return f'({opcode}) stores the result of register {rs1} - register {rs2} in register {rd}'
            elif opcode == 'fmul':
                return f'({opcode}) stores the result of register {rs1} * register {rs2} in register {rd}'
            elif opcode == 'fdiv':
                return f'({opcode}) stores the result of register {rs1} / register {rs2} in register {rd}'
        else:
            return f'({opcode}) stores the result of register {rs1} in  register {rd}'

# Example usage
instructions = parse_file('example.s')
inst = []
for i in instructions:
    inst.append(read_instruction(i))

# pygame setup
pygame.init()
screen_width = 1260
screen_height = 680
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
running = True
dt = 0

# Set up the colors
black = (0, 0, 0)
white = (255, 255, 255)

player_pos = pygame.Vector2(screen.get_width() // 2, screen.get_height() // 2)
i = 0

running = True
counter = 0  # This will increment with single W key presses

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Check for KEYDOWN event
        if event.type == pygame.KEYDOWN:
            # Check if the key pressed is W
            if event.key == pygame.K_w:
                counter += 1
                i = (i + 1) % len(inst)

    screen.fill(black)
    # Assuming player_pos is the center of the rectangle you want to draw
    # Calculate the top-left corner of the rectangle
    rect_x = player_pos.x# - 20  # 20 is half the width, to center the rectangle on player_pos.x
    rect_y = player_pos.y# - 20  # 20 is half the height, to center the rectangle on player_pos.y

    # Draw the rectangle
    # pygame.draw.rect(screen, "red", (rect_x - 400, rect_y - 50, 800, 100))


    # Prepare text
    font = pygame.font.Font(None, 30)
    # if i < len(inst):  # Check to avoid index error
    #     text = font.render(inst[i], True, white, "red")
    # else:
    #     text = font.render("End of instructions.", True, white, black)

    for k in range(len(inst)):
        text = font.render(inst[k], True, white, black)
        text_rect = text.get_rect()
        text_rect.center = (screen_width // 2, screen_height // 2 + k*20)

    # Blit text
        screen.blit(text, text_rect)

    # Optional: Update game screen, entities, etc. here

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()