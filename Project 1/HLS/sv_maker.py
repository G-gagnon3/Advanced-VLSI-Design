import typing

class builder():
    def __init__(self) -> None:
        self.lines = []
        self.pipeline = False
        self.filename = "test_FIR.sv"
        self.path = "HDL\\Filters\\"
        #self.file = self.start_file(self.path + self.filename)
        #self.block = Block()

    def start_file(self, file):
        return open(file, 'w')
    
    #def close_file(self):
    #    self.file.close()

    def generate_preamble(self):
        lines = []
        lines.append("`import ..\\Components\\All_Components.sv")
        return lines

    def write_file(self, top_level, preamble = False):
        lines = []
        if preamble:
            lines = self.generate_preamble()
        
        output =  "\n".join(lines) + "\n" + top_level.collapse()
        file = self.start_file(self.path + self.filename)
        file.write(output)
        file.close()

        return

class Block():
    def __init__(self, indent = "  "):
        self.lines = []
        self.middle_lines = []
        self.upper_stack = []
        self.lower_stack = []
        self.indent = indent
        return
    
    def insert_block(self, new_block):
        self.insert_lines(new_block.condense())
        return
    
    def condense(self):
        indented = [self.indent + line for line in self.middle_lines]
        self.lines = self.upper_stack[:] +  indented + self.lower_stack[::-1]
        return self.lines

    def collapse(self):
        self.condense()
        return "\n".join(self.lines)
    
    def insert_lines(self, lines):
        self.middle_lines += lines
        return

    def insert_upper_lines(self, lines):
        self.upper_stack += lines
        return
    
    def insert_lower_lines(self, lines):
        self.lower_stack += lines
        return
    

class Verilog_Module(Block):
    def __init__(self, name, ports, indent="  "):
        super().__init__(indent)
        self.generate_module_declaration(name, ports)
        
    def generate_module_declaration(self, name, ports):
        lines = []
        port_line = ", ".join([key + " " + ", ".join(ports[key]) for key in ports.keys()])
        lines.append(f"module {name} ({port_line});")

        end_lines = ["endmodule"]

        self.insert_upper_lines(lines)
        self.insert_lower_lines(end_lines)

class Always_FF(Block):
    def __init__(self, edges = None, indent="  "):
        super().__init__(indent)
        self.generate_declaration(edges)

    def generate_declaration(self, edges):
        if edges == None:
            edges = {"posedge": ["clk"], "negedge": ["reset"]}
        top_line = f"always_ff @({" or ".join([" or ".join([key + " " + value for value in edges[key]]) for key in edges.keys()])}) begin"
        bottom_line = "end"
        self.insert_upper_lines([top_line])
        self.insert_lower_lines([bottom_line])

class Always_Comb(Block):
    def __init__(self, indent="  "):
        super().__init__(indent)
        self.generate_declaration()

    def generate_declaration(self):
        top_line = f"always_comb begin"
        bottom_line = "end"
        self.insert_upper_lines([top_line])
        self.insert_lower_lines([bottom_line])

class Always_Latch(Block):
    def __init__(self, indent="  "):
        super().__init__(indent)

    def generate_declaration(self, values):
        if values == None:
            values = []
        top_line = f"always_latch ({" ".join(values)}) begin"
        bottom_line = "end"
        self.insert_upper_lines([top_line])
        self.insert_lower_lines([bottom_line])

class if_block(Block):
    def __init__(self, condition, indent="  "):
        super().__init__(indent)
        self.generate_declaration(condition)

    def generate_declaration(self, condition):
        top_line = f"if ({condition}) begin"
        bottom_line = "end"
        self.insert_upper_lines([top_line])
        self.insert_lower_lines([bottom_line])

class else_if_block(Block):
    def __init__(self, condition, indent="  "):
        super().__init__(indent)
        self.generate_declaration(condition)

    def generate_declaration(self, condition):
        top_line = f"else if ({condition}) begin"
        bottom_line = "end"
        self.insert_upper_lines([top_line])
        self.insert_lower_lines([bottom_line])

class else_block(Block):
    def __init__(self, indent="  "):
        super().__init__(indent)
        self.generate_declaration()

    def generate_declaration(self):
        top_line = "else begin"
        bottom_line = "end"
        self.insert_upper_lines([top_line])
        self.insert_lower_lines([bottom_line])

class FIR_Block(Verilog_Module):
    def __init__(self, name = "FIR", ports = None, indent="  "):
        if ports == None:
            ports = {"input logic": ["clk", "reset"], "input logic [15:0]": ["val_in"], "output logic [15:0]": ["val_out"]}
        super().__init__(name, ports, indent)
    
    def make_history_block(self):
        pass

    

    