from sv_maker import *
import math


def build_fir(taps):
    # Initialize object
    FIR = FIR_Block()

    # Make common logic
    FIR.insert_lines(make_common_logic(len(taps)))

    # Build the various blocks
    ## Build Tap Block
    FIR.insert_block(make_taps(taps))
    ## Build history block
    FIR.insert_block(make_history_buffer(len(taps)))
    FIR.insert_block(make_output_ffs(8))


    return FIR

def make_common_logic(num_taps):
    bits = 16
    lines = []
    lines.append(f"logic [{(num_taps-1)*bits-1}:0] history;")
    lines.append(f"logic [{num_taps*bits-1}:0] value_grid;")
    lines.append(f"logic [{bits-1}:0] cur_val_q;")
    lines.append(f"logic [{num_taps*bits-1}:0] tap_outputs;")
    lines.append(f"logic [{bits-1}:0] val_out_buffer;")
    lines.append("assign value_grid = {history, cur_val_q};")
    lines.append("assign cur_val_q = val_in;")
    
    return lines

def make_history_buffer(num_taps):
    hist_buff = Always_FF()
    c_bits = 16

    lines = []
    reset_blk = if_block("!reset")
    clk_blk = else_block()

    reset_blk.insert_lines([f"history = {{({(num_taps-1)*c_bits}){{1'b0}} }};"])
    #clk_blk.insert_lines(["history = {(history << 16), cur_val_q};"])
    clk_blk.insert_lines([f"history = (((history << {c_bits}) & {{{{{(num_taps-2)*c_bits}{{1'b1}}}}, {{{c_bits}{{1'b0}}}}}}) | cur_val_q);"])

    hist_buff.insert_block(reset_blk)
    hist_buff.insert_block(clk_blk)

    return hist_buff

def make_output_ffs(num_delays):
    output_buff = Always_FF()
    c_bits = 16
    lines = []

    lines.append(f"logic [{num_delays*c_bits-1}:0] val_out_buffer_int;")
    output_buff.insert_lines(lines)

    reset_blk = if_block("!reset")
    clk_blk = else_block()

    reset_blk.insert_lines([f"val_out_buffer_int = {{({(num_delays-1)*c_bits}){{1'b0}} }};"])
    #clk_blk.insert_lines(["history = {(history << 16), cur_val_q};"])
    clk_blk.insert_lines([f"val_out_buffer_int = (((val_out_buffer_int << {c_bits}) & {{{{{(num_delays-2)*c_bits}{{1'b1}}}}, {{{c_bits}{{1'b0}}}}}}) | val_out_buffer);"])
    clk_blk.insert_lines([f"val_out = val_out_buffer_int[{num_delays*c_bits-1}:{num_delays*c_bits-c_bits}]"])

    output_buff.insert_block(reset_blk)
    output_buff.insert_block(clk_blk)

    return output_buff

def make_tap_buffer(num_taps):
    tap_buff = Always_FF()
    c_bits = 16

    lines = []
    reset_blk = if_block("!reset")
    clk_blk = else_block()

    c_bits = 16
    # Do declarations
    lines = []
    ntaps = num_taps
    tiers = math.ceil(math.log2(ntaps))
    remaining_values = ntaps
    lines.append(f"logic [{remaining_values*c_bits-1}:0] adder_tree_tier_{0}_in;")
    for tier in range(tiers):
        output_values = remaining_values//2 + remaining_values%2
        lines.append(f"logic [{output_values*c_bits-1}:0] adder_tree_tier_{tier+1}_in;")
        remaining_values = output_values
    tap_block.insert_lines(lines)

    remaining_values = ntaps
    lines.append(f"logic [{remaining_values*c_bits-1}:0] adder_tree_tier_{0}_in;")
    for tier in range(tiers):
        output_values = remaining_values//2 + remaining_values%2
        lines.append(f"logic [{output_values*c_bits-1}:0] adder_tree_tier_{tier+1}_in;")
        remaining_values = output_values
    

    reset_blk.insert_lines([f"history = {{({(num_taps-1)*c_bits}){{1'b0}} }};"])
    #clk_blk.insert_lines(["history = {(history << 16), cur_val_q};"])
    clk_blk.insert_lines([f"history = (((history << {c_bits}) & {{{{{(num_taps-2)*c_bits}{{1'b1}}}}, {{{c_bits}{{1'b0}}}}}}) | cur_val_q);"])

    hist_buff.insert_block(reset_blk)
    hist_buff.insert_block(clk_blk)

    return hist_buff

def make_taps(taps):
    tap_block = Always_Comb()
    c_bits = 16
    # Do declarations
    lines = []
    ntaps = len(taps)
    tiers = math.ceil(math.log2(ntaps))
    remaining_values = ntaps
    lines.append(f"logic [{remaining_values*c_bits-1}:0] adder_tree_tier_{0}_in;")
    for tier in range(tiers):
        output_values = remaining_values//2 + remaining_values%2
        lines.append(f"logic [{output_values*c_bits-1}:0] adder_tree_tier_{tier+1}_in;")
        remaining_values = output_values
    tap_block.insert_lines(lines)
    

    # Do multiplication part
    def make_tap(value, tap_num):
        c_bits = 16
        intval = int(value)
        line = f"tap_outputs[{tap_num*c_bits + c_bits-1}:{tap_num*c_bits}] = value_grid[{tap_num*c_bits + c_bits-1}:{tap_num*c_bits}] * {intval};"
        return line
    
    lines = []
    for i, tap in enumerate(taps):
        lines.append(make_tap(tap, i))
    
    tap_block.insert_lines(lines)

    # Do adder tree
    lines = []
    ntaps = len(taps)
    tiers = math.ceil(math.log2(ntaps))
    remaining_values = ntaps
    #lines.append(f"logic [{remaining_values*c_bits-1}:0] adder_tree_tier_{0}_in;")
    lines.append(f"adder_tree_tier_{0}_in = tap_outputs;")

    for tier in range(tiers):
        output_values = remaining_values//2 + remaining_values%2
        #lines.append(f"logic [{output_values*c_bits-1}:0] adder_tree_tier_{tier+1}_in;")
        for output in range(remaining_values//2):
            lines.append(f"adder_tree_tier_{tier+1}_in[{output*c_bits + c_bits -1}:{output*c_bits}] = adder_tree_tier_{tier}_in[{output*2*c_bits + c_bits -1}:{output*2*c_bits}] + adder_tree_tier_{tier}_in[{output*2*c_bits + 2*c_bits -1 }:{output*2*c_bits + c_bits}];")
        if remaining_values % 2 == 1: # Extra value
            lines.append(f"adder_tree_tier_{tier+1}_in[{(output_values-1)*c_bits + c_bits -1}:{(output_values-1)*c_bits}] = adder_tree_tier_{tier}_in[{(output_values-1)*2*c_bits + c_bits -1}:{(output_values-1)*2*c_bits}];")
        remaining_values = output_values
    lines.append(f"val_out = adder_tree_tier_{tiers}_in;")
    tap_block.insert_lines(lines)

    return tap_block