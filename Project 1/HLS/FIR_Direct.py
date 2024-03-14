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


    return FIR

def make_common_logic(num_taps):
    lines = []
    lines.append(f"logic [{(num_taps-1)*16-1}:0] history;")
    lines.append(f"logic [{num_taps*16-1}:0] value_grid;")
    lines.append("logic [15:0] cur_val_q;")
    lines.append(f"logic [{num_taps*16-1}:0] tap_outputs;")
    lines.append("assign value_grid = {history, cur_val_q};")
    lines.append("assign cur_val_q = val_in;")
    
    return lines

def make_history_buffer(num_taps):
    hist_buff = Always_FF()

    lines = []
    reset_blk = if_block("!reset")
    clk_blk = else_block()

    reset_blk.insert_lines([f"history = {{({(num_taps-1)*16}){{1'b0}} }};"])
    #clk_blk.insert_lines(["history = {(history << 16), cur_val_q};"])
    clk_blk.insert_lines([f"history = (((history << 16) & {{{{{(num_taps-2)*16}{{1'b1}}}}, {{16{{1'b0}}}}}}) | cur_val_q);"])

    hist_buff.insert_block(reset_blk)
    hist_buff.insert_block(clk_blk)

    return hist_buff

def make_taps(taps):
    tap_block = Always_Comb()

    # Do multiplication part
    def make_tap(value, tap_num):
        intval = int(value)
        line = f"tap_outputs[{tap_num*16 + 15}:{tap_num*16}] = value_grid[{tap_num*16 + 15}:{tap_num*16}] * {intval};"
        return line
    
    lines = []
    for i, tap in enumerate(taps):
        lines.append(make_tap(tap, i))
    
    tap_block.insert_lines(lines)

    # Do adder tree
    ntaps = len(taps)
    #tiers = math.ceil(math.log2(ntaps))
    #remaining_values = ntaps
    #for tier in tiers:
    #    remaining_values = remaining_values//2 + remaining_values%1
    lines = ["val_out = " + " + ".join([f"tap_outputs[{i*16+15}:{i*16}]" for i in range(ntaps)]) + ";"]
    tap_block.insert_lines(lines)

    return tap_block