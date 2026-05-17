`default_nettype none
module present (
  input wire [79:0] key,
  input wire [63:0] pt,
  output wire [63:0] ct,

  input wire load,
  input wire clk,
  output wire busy
);
  function [3:0] one_sbox(input [3:0] in_);
    case (in_)
      4'h0 : one_sbox = 4'hC;
      4'h1 : one_sbox = 4'h5;
      4'h2 : one_sbox = 4'h6;
      4'h3 : one_sbox = 4'hB;
      4'h4 : one_sbox = 4'h9;
      4'h5 : one_sbox = 4'h0;
      4'h6 : one_sbox = 4'hA;
      4'h7 : one_sbox = 4'hD;
      4'h8 : one_sbox = 4'h3;
      4'h9 : one_sbox = 4'hE;
      4'hA : one_sbox = 4'hF;
      4'hB : one_sbox = 4'h8;
      4'hC : one_sbox = 4'h4;
      4'hD : one_sbox = 4'h7;
      4'hE : one_sbox = 4'h1;
      4'hF : one_sbox = 4'h2;
    endcase
  endfunction

  function [63:0] permute(input [63:0] in_);
    permute = {
      in_[63], in_[59], in_[55], in_[51], in_[47], in_[43], in_[39], in_[35],
      in_[31], in_[27], in_[23], in_[19], in_[15], in_[11], in_[ 7], in_[ 3],
      in_[62], in_[58], in_[54], in_[50], in_[46], in_[42], in_[38], in_[34],
      in_[30], in_[26], in_[22], in_[18], in_[14], in_[10], in_[ 6], in_[ 2],
      in_[61], in_[57], in_[53], in_[49], in_[45], in_[41], in_[37], in_[33],
      in_[29], in_[25], in_[21], in_[17], in_[13], in_[ 9], in_[ 5], in_[ 1],
      in_[60], in_[56], in_[52], in_[48], in_[44], in_[40], in_[36], in_[32],
      in_[28], in_[24], in_[20], in_[16], in_[12], in_[ 8], in_[ 4], in_[ 0]
    };
  endfunction

  reg [4:0] rnd;
  reg [79:0] key_reg;
  reg [63:0] state;

  wire [63:0] ark_o;
  assign ark_o = state ^ key_reg[79:16];
  assign ct = ark_o;

  wire [63:0] sbox_o;
  genvar sbox_i;
  generate
    for (sbox_i = 0; sbox_i < 64; sbox_i = sbox_i + 4) begin
      assign sbox_o[sbox_i+3:sbox_i] = one_sbox(ark_o[sbox_i+3:sbox_i]);
    end
  endgenerate

  wire[63:0] permute_o;
  assign permute_o = permute(sbox_o);

  wire [79:0] key_shift = {key_reg[18:0], key_reg[79:19]};
  wire [79:0] key_next;
  assign key_next = {
    one_sbox(key_shift[79:76]),
    key_shift[75:20],
    key_shift[19:15] ^ rnd,
    key_shift[14:0]
  };

  assign busy = (rnd != 0);

  always @(posedge clk) begin
    if (load) begin: p_present_init
      rnd <= 1;
      key_reg <= key;
      state <= pt;
    end else if (rnd != 0) begin: p_present_encrypt
      rnd <= rnd + 1;
      key_reg <= key_next;
      state <= permute_o;
    end
  end
endmodule
