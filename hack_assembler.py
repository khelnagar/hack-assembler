import sys
import re
import itertools
import collections



"""

The input file is Hack assembly language instructions file 
made as part of nand2tetris online course on Coursera.

It translates Hack assembly instructions to binary code. This 
binary code runs on the Hack computer architecture developed 
during the course. 

Ex terminal command to run the assembler:
"python hack_assembler.py max\\Max.asm"

where max\\Max.asm is the path to the assembly file relative
to the root of script hack_assembler.py

the output is a .hack file with path max\\Max.hack 

"""

# the assembly file path is passed as a command line argument   
input_file = sys.argv[1]

# the result text to be written in output hack file
hack_text = []


COMP = collections.namedtuple('COMP', 'a c')
COMP_DICT = {
	'0': COMP(0, '101010'),
	'1': COMP(0, '111111'),
	'-1': COMP(0, '111010'),
	'D': COMP(0, '001100'),
	'A': COMP(0, '110000'),
	'!D': COMP(0, '001101'),
	'!A': COMP(0, '110001'),
	'-D': COMP(0, '001111'),
	'-A': COMP(0, '110011'),
	'D+1': COMP(0, '011111'),
	'A+1': COMP(0, '110111'),
	'D-1': COMP(0, '001110'),
	'A-1': COMP(0, '110010'),
	'D+A': COMP(0, '000010'),
	'D-A': COMP(0, '010011'),
	'A-D': COMP(0, '000111'),
	'D&A': COMP(0, '000000'),
	'D|A': COMP(0, '010101'),
	'M': COMP(1, '110000'),
	'!M': COMP(1, '110001'),
	'-M': COMP(1, '110011'),
	'M+1': COMP(1, '110111'),
	'M-1': COMP(1, '110010'),
	'D+M': COMP(1, '000010'),
	'D-M': COMP(1, '010011'),
	'M-D': COMP(1, '000111'),
	'D&M': COMP(1, '000000'),
	'D|M': COMP(1, '010101')
}

DEST_DICT = {
	'M': '001',
	'D': '010',
	'MD': '011',
	'A': '100',
	'AM': '101',
	'AD': '110',
	'AMD': '111',
	None: '000'
}

JUMP_DICT = {
	'JGT': '001',
	'JEQ': '010',
	'JGE': '011',
	'JLT': '100',
	'JNE': '101',
	'JLE': '110',
	'JMP': '111',
	None: '000'
}

SYMBOLIC_TABLE = {
	'R0': 0,
	'R1': 1,
	'R2': 2,
	'R3': 3,
	'R4': 4,
	'R5': 5,
	'R6': 6,
	'R7': 7,
	'R8': 8,
	'R9': 9,
	'R10': 10,
	'R11': 11,
	'R12': 12,
	'R13': 13,
	'R14': 14,
	'R15': 15,
	'SCREEN': 16384,
	'KBD': 24576,
	'SP': 0,
	'LCL': 1,
	'ARG': 2,
	'THIS': 3,
	'THAT': 4
}

def is_comment_line(line):
	return line.startswith('/')

def is_empty_line(line):
	return not line.strip()

def is_label_line(line):
	return line.startswith('(')


def get_or_add_variable(line):
	"""returns an integer value for the variable whether 
	it's a new declared one or already in the symbolic table"""
	
	# 16 is chosen by assembly language design to be first variable 
	# address allocated in memory 
	address_counter = itertools.count(16, 1)

	variable = line[1:]
	address = SYMBOLIC_TABLE.get(variable, next(address_counter))

	return address

def get_A_binary_code(line):
	"""returns a 15-bit of the integer with 0 at the start of A instruction"""
	
	return '0' + format(int(line[1:]), '015b')

def get_C_binary_code(line):
	"""returns 13-bit concatenation of dest = comp ; jump 
	with 111 at the start of C instruction"""

	dest =  re.search(r'([AMD]+)?=?([AMD\d\-+&|!]+);?([A-Z]+)?', line).group(1)
	comp =  re.search(r'([AMD]+)?=?([AMD\d\-+&|!]+);?([A-Z]+)?', line).group(2)
	jump =  re.search(r'([AMD]+)?=?([AMD\d\-+&|!]+);?([A-Z]+)?', line).group(3)

	return '111' + f'{COMP_DICT[comp].a}{COMP_DICT[comp].c}{DEST_DICT[dest]}{JUMP_DICT[jump]}'

# first pass to put labels in symbolic table
with open(input_file) as assembly_text:
	line_counter = 0
	for line in assembly_text:
		# ignore comments and white spaces lines
		if is_comment_line(line) or is_empty_line(line):
			continue

		strip_line = line.strip()
		if strip_line.startswith('('):
			label = strip_line[1:-1]
			SYMBOLIC_TABLE[label] = line_counter
			# do not increment the counter, as label line is bypassed
			continue

		line_counter += 1

# second pass to do the actual assembler translation
with open(input_file) as assembly_text:
	for line in assembly_text:
		# ignore comments and white spaces lines
		if is_comment_line(line) or is_empty_line(line) or is_label_line(line):
			continue

		# handling inline comments
		strip_line = line.split('/')[0].strip()

		# handling A instruction
		if strip_line.startswith('@'):
			try:
				# if it's integer address
				int(strip_line[1:])
			except ValueError:
				variable_address = get_or_add_variable(strip_line)
				strip_line = f'@{variable_address}'
			binary_line = get_A_binary_code(strip_line)
		else:
			# handling C instruction
			binary_line = get_C_binary_code(strip_line)

		hack_text.append(binary_line)

# writing to a .hack file
with open(input_file.split('.')[0] + '.hack', 'w') as f:
    for line in hack_text:
        f.write(f'{line}\n')
