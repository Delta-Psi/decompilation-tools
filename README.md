# Decompilaton tools
A set of utilities designed towards manual decompilation of x86-64 binaries.

## gdb\_commands.py
A Python script containing command definitions usable in GDB. Load them with `source <path to gdb_commands.py>`. It requires the following packages:
* `networkx`

### build-jump-graph
Generates a GraphML file from the flow graph of the dissasembly of function. Usage: `build-jump-graph <location> <output>` where `<location>` is either a function symbol or an address preceded by `*`. The GraphML file will be written to `<output>`, relative to the GDB working directory.

The resulting file will contain a directed graph with one node for each relevant disassembled section. Each one will have the following attributes:
* `entry_point` (boolean): whether the node is the entry point of the function.
* `returns` (boolean): whether the node is a return point.
* `asm` (string): the disassembly of the node.

Each node will have up to two outgoing edges; one represents regular program flow and one represents a (conditional or unconditional) jump. This distinction is made through the `jump` attribute. It should be noted that every node will end in either a jump or a return instruction.

One can use the free tool [yed][https://www.yworks.com/products/yed] to visualize the resulting network. A decent layout can be obtained by:
1. Selecting every node (Control+A) and setting both left alignment and a monospaced font family in the properties view.
1. Importing the mapping configurations in `yed_node.cnfx` and `yed_edge.cnfx` through `Edit > Properties Mapper...`.
1. Applying the previous configurations.
1. Generating a flowchart layout through `Layout > Flowchart` with the default options.

The result should be something like this: ![yed window displaying disassembly graph][images/yed_result.png].
