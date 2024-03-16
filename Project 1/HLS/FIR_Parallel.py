from sv_maker import *
import math


def build_fir(taps, parallelization, c_bits):
    # Initialize object
    ports = {"input logic": ["clk", "reset"], f"input logic [{(parallelization*c_bits)-1}:0]": ["val_in"], f"output logic [{(parallelization*c_bits)-1}:0]": ["val_out"]}
    FIR = FIR_Block(ports=ports)

    # Make common logic
    FIR.insert_lines(make_common_logic(len(taps),parallelization,c_bits))

    # Build the various blocks
    ## Build Tap Block
    FIR.insert_block(make_taps(taps, parallelization, c_bits))
    ## Build history block
    FIR.insert_block(make_history_buffer(len(taps), parallelization, c_bits))
    FIR.insert_lines(make_output_direct(c_bits))


    return FIR

def make_common_logic(num_taps, parallelization, bits):
    lines = []
    per_parallel_delays = math.ceil((num_taps-1)/parallelization)
    lines.append(f"logic [{per_parallel_delays*bits-1}:0] history;")
    lines.append(f"logic [{((per_parallel_delays+2)*parallelization)*bits + parallelization*bits + bits-1}:0] value_grid;")
    lines.append(f"logic [{parallelization*bits-1}:0] cur_val_q;")
    lines.append(f"logic [{parallelization*num_taps*bits-1}:0] tap_outputs;")
    lines.append(f"logic [{parallelization*bits-1}:0] val_out_buffer;")
    lines.append("assign value_grid = {history, cur_val_q};")
    lines.append("assign cur_val_q = val_in;")
    
    return lines

def make_history_buffer(num_taps, parallelization, c_bits):
    hist_buff = Always_FF()

    lines = []
    reset_blk = if_block("!reset")
    clk_blk = else_block()

    shiftval = c_bits * parallelization
    total_hist_size = (math.ceil((num_taps-1)/3))*c_bits
    mask_size = c_bits * parallelization # Same as shiftval but ig a little clearer

    reset_blk.insert_lines([f"history = {{({total_hist_size}){{1'b0}} }};"])
    #clk_blk.insert_lines(["history = {(history << 16), cur_val_q};"])
    clk_blk.insert_lines([f"history = (((history << {shiftval}) & {{{{{total_hist_size-mask_size}{{1'b1}}}}, {{{mask_size}{{1'b0}}}}}}) | cur_val_q);"])

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

def make_output_direct(c_bits):
    lines = []

    lines.append(f"assign val_out = val_out_buffer;")
    return lines

def make_taps(taps, parallelization, c_bits):
    tap_block = Always_Comb()
    # Do declarations
    lines = []
    ntaps = len(taps)
    tiers = math.ceil(math.log2(ntaps))
    remaining_values = ntaps
    for parallel_num in range(parallelization):
        remaining_values = ntaps
        lines.append(f"logic [{remaining_values*c_bits-1}:0] adder_tree_tier_{0}_p{parallel_num}_in;")
        for tier in range(tiers):
            output_values = remaining_values//2 + remaining_values%2
            lines.append(f"logic [{output_values*c_bits-1}:0] adder_tree_tier_{tier+1}_p{parallel_num}_in;")
            remaining_values = output_values
    tap_block.insert_lines(lines)
    

    # Do multiplication part
    def make_tap(value, parallel, n_parallel, tap_num, c_bits, n_taps):
        intval = int(value)
        history_parallel_stride = n_parallel * c_bits
        is_over_threshold = ((tap_num%n_parallel)) <= n_parallel-parallel
        history_tap_offset = 0
        if is_over_threshold:
            history_tap_offset = 1
        history_addr = history_parallel_stride*(parallel+ history_tap_offset) + c_bits*tap_num
        
        # Scratch work:
        # 0->0: 0, n-1, n-2,...
        # 0->1: 1, 0, n-1, ...
        # (tap + parallel) % n_parallel = p_tier
        # 
        p_tier = (tap + parallel) % n_parallel
        output_parallel_stride = n_taps * c_bits
        output_tap_stride = c_bits
        tap_outputs_addr = p_tier * output_parallel_stride + tap_num * output_tap_stride 
        # The above line of code is a bit wonky, but it aligns the data such that contiguous bits are for the same output
        line = f"tap_outputs[{tap_outputs_addr + c_bits-1}:{tap_outputs_addr}] = value_grid[{history_addr + c_bits-1}:{history_addr}] * {intval};"
        return line
    
    lines = []
    for parallel in range(parallelization):
        for i, tap in enumerate(taps):
            lines.append(make_tap(tap, parallel, parallelization, i, c_bits, len(taps)))
        
    tap_block.insert_lines(lines)

    # Do adder tree
    lines = []
    ntaps = len(taps)
    tiers = math.ceil(math.log2(ntaps))
    remaining_values = ntaps
    #lines.append(f"logic [{remaining_values*c_bits-1}:0] adder_tree_tier_{0}_in;")

    output_parallel_stride = ntaps * c_bits
    for parallel_num in range(parallelization):
        lines.append(f"adder_tree_tier_{0}_p{parallel_num}_in = tap_outputs[{output_parallel_stride*(parallel_num+1)-1}:{output_parallel_stride*parallel_num}];")
        remaining_values = ntaps # Reset on every pass

        for tier in range(tiers):
            output_values = remaining_values//2 + remaining_values%2
            #lines.append(f"logic [{output_values*c_bits-1}:0] adder_tree_tier_{tier+1}_in;")
            for output in range(remaining_values//2):
                lines.append(f"adder_tree_tier_{tier+1}_p{parallel_num}_in[{output*c_bits + c_bits -1}:{output*c_bits}] = adder_tree_tier_{tier}_p{parallel_num}_in[{output*2*c_bits + c_bits -1}:{output*2*c_bits}] + adder_tree_tier_{tier}_p{parallel_num}_in[{output*2*c_bits + 2*c_bits -1 }:{output*2*c_bits + c_bits}];")
            if remaining_values % 2 == 1: # Extra value
                lines.append(f"adder_tree_tier_{tier+1}_p{parallel_num}_in[{(output_values-1)*c_bits + c_bits -1}:{(output_values-1)*c_bits}] = adder_tree_tier_{tier}_p{parallel_num}_in[{(output_values-1)*2*c_bits + c_bits -1}:{(output_values-1)*2*c_bits}];")
            remaining_values = output_values
        lines.append(f"val_out_buffer[{parallel_num*c_bits+c_bits-1}:{parallel_num*c_bits}] = adder_tree_tier_{tiers}_p{parallel_num}_in;")
    tap_block.insert_lines(lines)

    return tap_block