`define T0 1
`define T1 1
`define T2 1
`define T3 1

module FIR #(
    parameter CALC_BITS = 16,
    parameter IO_BITS = 32,
    parameter N_TAPS = 4
) (
    input logic clk, reset,
    input logic [IO_BITS-1:0] val_in,
    output logic [IO_BITS-1:0] val_out);

    logic [N_TAPS-2:0] [CALC_BITS-1:0] history;
    logic [N_TAPS-1:0] [CALC_BITS-1:0] val_array;
    logic [CALC_BITS-1:0] cur_val_q;

    logic [N_TAPS-1:0] [CALC_BITS-1:0] tap_outputs;

    assign val_array = {history, cur_val_q};

    always_ff @( posedge clk or negedge reset ) begin : ValueHistory
        // History shift
        if (clk) begin
            history = {(history << CALC_BITS), cur_val_q};
        end

        // Reset / initialize
        if (!reset) begin
            history = {{(N_TAPS-1)*CALC_BITS{1'b0}}};
        end
        
    end

    always_comb begin : Tap_Calcs
        // Multiplies
        tap_outputs[0] = T0 * val_array[0];
        tap_outputs[1] = T1 * val_array[1];
        tap_outputs[2] = T2 * val_array[2];
        tap_outputs[3] = T3 * val_array[3];

        val_out = (tap_outputs[0] + tap_outputs[1] + tap_outputs[2] + tap_outputs[3]) << 16;
    end


endmodule