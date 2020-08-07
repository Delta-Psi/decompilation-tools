import re
from collections import deque
import networkx

class JumpGraph(gdb.Command):
    def __init__(self):
        super().__init__("jump_graph", gdb.COMMAND_DATA, gdb.COMPLETE_LOCATION)

    def invoke(self, args, from_tty):
        argv = gdb.string_to_argv(args)
        symbol = gdb.parse_and_eval(argv[0])
        jump_graph(int(symbol.address), argv[1])
JumpGraph()

def jump_graph(address, outpath):
    bfs = deque([address])
    visited = set()
    def push_to_queue(addr):
        if not addr in visited:
            bfs.appendleft(addr)
            visited.add(addr)
    boundaries = set([address])

    while len(bfs) > 0:
        addr = bfs.pop()
        _, jump_addr, next_addr = parse_i(addr)
        if jump_addr is not None:
            boundaries.add(jump_addr)
            push_to_queue(jump_addr)
            if next_addr is not None:
                boundaries.add(next_addr)
        if next_addr is not None:
            push_to_queue(next_addr)

    graph = networkx.DiGraph()
    for addr in boundaries:
        asm = ''
        current_addr = addr
        while current_addr is not None:
            instr, jump_addr, next_addr = parse_i(current_addr)
            asm += instr + '\n'

            if jump_addr is not None:
                graph.add_edge(addr, jump_addr, jump=True)
            if next_addr in boundaries:
                graph.add_edge(addr, next_addr, jump=False)
                break
            current_addr = next_addr

        graph.add_node(addr, asm=asm)
    networkx.write_graphml(graph, outpath)

instruction = re.compile("""\s*0x([0-9a-f]*).*?:\s*(.*?)\s*\n""")
jump1 = re.compile("""(j[a-z]*)\s*0x([0-9a-f]*)""")
jump2 = re.compile("""(j[a-z]*)\s*.*?# 0x([0-9a-f]*)""")

# returns (instr as str, jump addr or none, addr of next instr or none if ret/jmp)
def parse_i(address):
    string = gdb.execute('x/2i 0x{:x}'.format(address), to_string=True)
    full_instr = string.split('\n')[0]
    first, second = re.findall(instruction, string)

    instr = first[1]
    if instr.startswith("ret"):
        return full_instr, None, None

    jump_addr = None
    jump_match = re.match(jump1, instr) or re.match(jump2, instr)
    if jump_match is not None:
        jump_addr = int(jump_match[2], 16)

        if jump_match[1] == "jmp":
            return full_instr, jump_addr, None

    next_addr = int(second[0], 16)
    return full_instr, jump_addr, next_addr
