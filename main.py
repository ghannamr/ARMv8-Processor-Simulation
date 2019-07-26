def parse_instruction(fullInstruction): # Function that takes in the one line instruction and parses it into an array if strings
    operation = fullInstruction.split()
    operationRefined = []
    for element in operation:
        operationRefined.append(element.strip(",").strip("[").strip("]"))
    return operationRefined

def instruction_fetch_step(operation): # Function that takes in the parsed instruction and returns the RegisterControl, ALUcontrol, MemoryControl, BranchControl, and WritebackControl
    if operation[0] == 'ADD':
        return ['using2', 'addition', 'unused', 'unused', 'used']
    if operation[0] == 'SUB':
        return ['using2', 'subtraction', 'unused', 'unused', 'used']
    if operation[0] == 'ADDI':
        return ['using1', 'additionImmediate', 'unused', 'unused', 'used']
    if operation[0] == 'SUBI':
        return ['using1', 'subtractionImmediate', 'unused', 'unused', 'used']
    if operation[0] == 'LDUR':
        return ['using1', 'additionImmediate', 'usedread', 'unused', 'usedload']
    if operation[0] == 'STUR':
        return ['using2store', 'additionImmediate', 'usedwrite', 'unused', 'unused']
    if operation[0] == 'CBZ':
        return ['using1conditional', 'unused', 'unused', 'usedconditional', 'unused']
    if operation[0] == 'B':
        return ['using0', 'unused', 'unused', 'usedbranch', 'unused']

def register_step(operation, control): #the register step uses only the first bit of control, which means control[0]
    if control[0] == 'using2': #if the control says to use Rt and Rm
        #if the register is XZR, the input is 0, else it's the register number
        first = 0 if operation[2] == 'XZR' else registers[int(operation[2][1:])] #this is the first register value returned
        second = 0 if operation[3] == 'XZR' else registers[int(operation[3][1:])] #this is the second register value returned
        return [first, second] #returns the value in the registers
    elif control[0] == 'using2store': #particular case for store
        first = 0 if operation[2] == 'XZR' else registers[int(operation[2][1:])] #this is the first register value returned
        second = 0 if operation[1] == 'XZR' else registers[int(operation[1][1:])] #this is the first register value returned
        return [first, second]
    elif control[0] == 'using1':
        #if the register is XZR, the input is 0, else it's the register number
        first = 0 if operation[2] == 'XZR' else registers[int(operation[2][1:])] #this is the first register value returned
        return [first]
    elif control[0] == 'using1conditional': #particular case for conditionals
        first = 0 if operation[1] == 'XZR' else registers[int(operation[1][1:])] #this is the first register value returned
        return [first]
    elif control[0] == 'using0': #this happens for branch instructions
        return []

def execute_step(operation, registerOutput, control): #the execute step uses only the second bit of control, which means control[1]
    if control[1] == 'addition':
        return (registerOutput[0] + registerOutput[1])
    elif control[1] == 'subtraction':
        return (registerOutput[0] - registerOutput[1])
    elif control[1] == 'additionImmediate':
        immediate = int(operation[3][1:])
        return (registerOutput[0] + immediate)
    elif control[1] == 'subtractionImmediate':
        immediate = int(operation[3][1:])
        return (registerOutput[0] - immediate)
    elif control[1] == 'unused':
        return 0

def memory_step(registerOutput, ALUOutput, control): #the memory step uses the third bit of control, which is control[2]
    if control[2] == 'usedread': #if it's a read instruction, the data from memory is simply returned
        return memory[ALUOutput]
    elif control[2] == 'usedwrite': #if it's a write, 0 is returned and the memory takes the value of the register
        print(registerOutput[0])
        memory[ALUOutput] = registerOutput[1]
        return 0
    elif control[2] == 'unused':
        return 0

def PC_step(operation, registerOutput, control): #the PC step uses the fourth bit of control, which is control[3]. Note that this step is not part of the pipeline: it determines the value of PC after every iteration
    if control[3] == 'usedconditional':
        if registerOutput[0] == 0: #if the condition is met when the register value is 0
            return int(operation[2])
        else: #if it's not simply return an increment of 1
            return 1
    elif control[3] == 'usedbranch': #if it's a branch, increment PC by the branch offset
        return int(operation[1])
    elif control[3] == 'unused': #if there is no branch, increment PC by 1
        return 1

def writeback_step(operation, ALUOutput, memoryOutput, control): #the writeback step uses the fifth bit of control, which is control[4]
    if control[4] == 'used': #this case happens when writing back after a standard R or I type
        registerNumber = int(operation[1][1:]) #the register number is the register to writeback to
        registers[registerNumber] = ALUOutput
        return
    elif control[4] == 'usedload': #the only case this happens is during STUR instructions
        registerNumber = int(operation[1][1:]) #the register number is the register to writeback to
        registers[registerNumber] = memoryOutput
        return
    elif control[4] == 'unused': #don't do anything if it's unused
        return




example = open("example3.txt", "r")
instructions = []
# Populating the instruction register
for line in example:
    instructions.append(line.strip("\n"))
#print(instructionRegister)

instructionRegister = []    # holds all the instructions

for instruction in instructions:
    # parse the instruction
    operation = parse_instruction(instruction) #returns an array of the elements of the instruction: operation[0] is always the opcode, operation[1:3] are registers / immediates
    instructionRegister.append(operation)


# Processor components
registers = [0] * 31        # holds the register values
memory = [0] * 10           # holds the processor's memory (usually a lot bigger but it's small for this example)
memory[0] = 10
memory[1] = 13              # hard coding the memory values for example2.txt
PC = 0                      # value of the program counter

while PC < len(instructionRegister):
    # fetch the instruction and determine the control bits
    control = instruction_fetch_step(instructionRegister[PC])
    # get values from the registers
    registerOutput = register_step(instructionRegister[PC], control)
    # execute instructions
    ALUOutput = execute_step(instructionRegister[PC], registerOutput, control)
    # access memory
    memoryOutput = memory_step(registerOutput, ALUOutput, control)
    # write back
    writeback_step(instructionRegister[PC], ALUOutput, memoryOutput, control)
    #print everything in console for a reference
    print("current instruction:")
    print(instructionRegister[PC])
    print("registers: ")
    print(registers)
    print("memory: ")
    print(memory)
    print('--------------------------------------------------------------------')
    # change the PC number
    PC += PC_step(instructionRegister[PC], registerOutput, control)
