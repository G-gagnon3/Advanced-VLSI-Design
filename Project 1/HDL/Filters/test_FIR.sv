
module FIR (input logic clk, reset, input logic [15:0] val_in, output logic [15:0] val_out);
  logic [495:0] history;
  logic [511:0] value_grid;
  logic [15:0] cur_val_q;
  logic [511:0] tap_outputs;
  assign value_grid = {history, cur_val_q};
  assign cur_val_q = val_in;
  always_comb begin
    tap_outputs[15:0] = value_grid[15:0] * 0;
    tap_outputs[31:16] = value_grid[31:16] * 1;
    tap_outputs[47:32] = value_grid[47:32] * 2;
    tap_outputs[63:48] = value_grid[63:48] * 3;
    tap_outputs[79:64] = value_grid[79:64] * 4;
    tap_outputs[95:80] = value_grid[95:80] * 5;
    tap_outputs[111:96] = value_grid[111:96] * 6;
    tap_outputs[127:112] = value_grid[127:112] * 7;
    tap_outputs[143:128] = value_grid[143:128] * 8;
    tap_outputs[159:144] = value_grid[159:144] * 9;
    tap_outputs[175:160] = value_grid[175:160] * 10;
    tap_outputs[191:176] = value_grid[191:176] * 11;
    tap_outputs[207:192] = value_grid[207:192] * 12;
    tap_outputs[223:208] = value_grid[223:208] * 13;
    tap_outputs[239:224] = value_grid[239:224] * 14;
    tap_outputs[255:240] = value_grid[255:240] * 15;
    tap_outputs[271:256] = value_grid[271:256] * 16;
    tap_outputs[287:272] = value_grid[287:272] * 17;
    tap_outputs[303:288] = value_grid[303:288] * 18;
    tap_outputs[319:304] = value_grid[319:304] * 19;
    tap_outputs[335:320] = value_grid[335:320] * 20;
    tap_outputs[351:336] = value_grid[351:336] * 21;
    tap_outputs[367:352] = value_grid[367:352] * 22;
    tap_outputs[383:368] = value_grid[383:368] * 23;
    tap_outputs[399:384] = value_grid[399:384] * 24;
    tap_outputs[415:400] = value_grid[415:400] * 25;
    tap_outputs[431:416] = value_grid[431:416] * 26;
    tap_outputs[447:432] = value_grid[447:432] * 27;
    tap_outputs[463:448] = value_grid[463:448] * 28;
    tap_outputs[479:464] = value_grid[479:464] * 29;
    tap_outputs[495:480] = value_grid[495:480] * 30;
    tap_outputs[511:496] = value_grid[511:496] * 31;
    val_out = tap_outputs[15:0] + tap_outputs[31:16] + tap_outputs[47:32] + tap_outputs[63:48] + tap_outputs[79:64] + tap_outputs[95:80] + tap_outputs[111:96] + tap_outputs[127:112] + tap_outputs[143:128] + tap_outputs[159:144] + tap_outputs[175:160] + tap_outputs[191:176] + tap_outputs[207:192] + tap_outputs[223:208] + tap_outputs[239:224] + tap_outputs[255:240] + tap_outputs[271:256] + tap_outputs[287:272] + tap_outputs[303:288] + tap_outputs[319:304] + tap_outputs[335:320] + tap_outputs[351:336] + tap_outputs[367:352] + tap_outputs[383:368] + tap_outputs[399:384] + tap_outputs[415:400] + tap_outputs[431:416] + tap_outputs[447:432] + tap_outputs[463:448] + tap_outputs[479:464] + tap_outputs[495:480] + tap_outputs[511:496];
  end
  always_ff @(posedge clk or negedge reset) begin
    if (!reset) begin
      history = {(496){1'b0} };
    end
    else begin
      history = (((history << 16) & {{480{1'b1}}, {16{1'b0}}}) | cur_val_q);
    end
  end
endmodule