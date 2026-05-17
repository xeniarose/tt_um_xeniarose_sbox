/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */
// `timescale 1ns / 1ps
`default_nettype none

module tt_um_xeniarose_sbox (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
  wire _unused = &{ena, 1'b0};

  wire [5:0] io_addr = ui_in[5:0];
  wire io_we = ui_in[6];
  wire io_clk = ui_in[7];

  reg io_ready;
  wire trig;

  assign uo_out[0] = io_ready;
  assign uo_out[1] = io_we;
  assign uo_out[2] = trig;

  assign uo_out[7:3] = 5'h0;

  assign uio_oe[0] = io_we;
  assign uio_oe[1] = io_we;
  assign uio_oe[2] = io_we;
  assign uio_oe[3] = io_we;
  assign uio_oe[4] = io_we;
  assign uio_oe[5] = io_we;
  assign uio_oe[6] = io_we;
  assign uio_oe[7] = io_we;

  reg [7:0] io_out;
  assign uio_out = io_out;

  (* mem2reg *)
  reg [7:0] register_file [29:0];

  initial begin
    $dumpfile("tb.fst");
    $dumpvars(0, tt_um_xeniarose_sbox);
    $dumpvars(0, register_file[0]);
    $dumpvars(0, register_file[1]);
    $dumpvars(0, register_file[2]);
    $dumpvars(0, register_file[3]);
    $dumpvars(0, register_file[4]);
    $dumpvars(0, register_file[5]);
    $dumpvars(0, register_file[6]);
    $dumpvars(0, register_file[7]);
    $dumpvars(0, register_file[8]);
    $dumpvars(0, register_file[9]);
    $dumpvars(0, register_file[10]);
    $dumpvars(0, register_file[11]);
    $dumpvars(0, register_file[12]);
    $dumpvars(0, register_file[13]);
    $dumpvars(0, register_file[14]);
    $dumpvars(0, register_file[15]);
    $dumpvars(0, register_file[16]);
    $dumpvars(0, register_file[17]);
    $dumpvars(0, register_file[18]);
    $dumpvars(0, register_file[19]);
    $dumpvars(0, register_file[20]);
    $dumpvars(0, register_file[21]);
    $dumpvars(0, register_file[22]);
    $dumpvars(0, register_file[23]);
    $dumpvars(0, register_file[24]);
    $dumpvars(0, register_file[25]);
    $dumpvars(0, register_file[26]);
    $dumpvars(0, register_file[27]);
    $dumpvars(0, register_file[28]);
    $dumpvars(0, register_file[29]);
  end

  reg [1:0] run_sbox;
  reg run_sbox_next;
  reg run_present_next;

  assign trig = (run_sbox != 2'b00);

  wire [7:0] sbox0_in;
  wire [7:0] sbox0_out;
  wire [7:0] sbox1_in;
  wire [7:0] sbox1_out;
  wire [7:0] sbox2_in;
  wire [7:0] sbox2_out;
  wire [7:0] sbox3_in;
  wire [7:0] sbox3_out;

  aes_sbox sbox0 (
    .U(sbox0_in),
    .dec(1'b0),
    .S(sbox0_out)
  );

  aes_sbox sbox1 (
    .U(sbox1_in),
    .dec(1'b0),
    .S(sbox1_out)
  );

  aes_sbox sbox2 (
    .U(sbox2_in),
    .dec(1'b0),
    .S(sbox2_out)
  );

  aes_sbox sbox3 (
    .U(sbox3_in),
    .dec(1'b0),
    .S(sbox3_out)
  );

  assign sbox0_in =
    (run_sbox == 2'b01 ? register_file[0] :
    (run_sbox == 2'b10 ? register_file[0] ^ register_file[4] : 8'h00));

  assign sbox1_in =
    (run_sbox == 2'b01 ? register_file[1] :
    (run_sbox == 2'b10 ? register_file[1] ^ register_file[5] : 8'h00));

  assign sbox2_in =
    (run_sbox == 2'b01 ? register_file[2] :
    (run_sbox == 2'b10 ? register_file[2] ^ register_file[6] : 8'h00));

  assign sbox3_in =
    (run_sbox == 2'b01 ? register_file[3] :
    (run_sbox == 2'b10 ? register_file[3] ^ register_file[7] : 8'h00));

  wire [63:0] present_ct;
  present present_inst (
    .clk(clk),
    .load(run_present_next),
    .key({register_file[21], register_file[20], register_file[19], register_file[18], register_file[17], register_file[16], register_file[15], register_file[14], register_file[13], register_file[12]}),
    .pt({register_file[29], register_file[28], register_file[27], register_file[26], register_file[25], register_file[24],register_file[23], register_file[22]}),
    .ct(present_ct)
  );

  always @(posedge clk or negedge rst_n) begin : p_main
    if (!rst_n) begin
      register_file[0] <= 8'h0;
      register_file[1] <= 8'h0;
      register_file[2] <= 8'h0;
      register_file[3] <= 8'h0;
      register_file[4] <= 8'h0;
      register_file[5] <= 8'h0;
      register_file[6] <= 8'h0;
      register_file[7] <= 8'h0;
      register_file[8] <= 8'h0;
      register_file[9] <= 8'h0;
      register_file[10] <= 8'h0;
      register_file[11] <= 8'h0;
      register_file[12] <= 8'h0;
      register_file[13] <= 8'h0;
      register_file[14] <= 8'h0;
      register_file[15] <= 8'h0;
      register_file[16] <= 8'h0;
      register_file[17] <= 8'h0;
      register_file[18] <= 8'h0;
      register_file[19] <= 8'h0;
      register_file[20] <= 8'h0;
      register_file[21] <= 8'h0;
      register_file[22] <= 8'h0;
      register_file[23] <= 8'h0;
      register_file[24] <= 8'h0;
      register_file[25] <= 8'h0;
      register_file[26] <= 8'h0;
      register_file[27] <= 8'h0;
      register_file[28] <= 8'h0;
      register_file[29] <= 8'h0;

      io_out <= 8'h0;
      io_ready <= 1'b0;

      run_sbox <= 2'b0;
      run_sbox_next <= 1'b0;
      run_present_next <= 1'b0;
    end else begin
      io_ready <= 1;

      if (io_clk) begin
        if (!io_we) begin
          case (io_addr)
            63: begin
              run_sbox_next <= 1'b1;
            end
            62: begin
              run_present_next <= 1'b1;
            end

            default: begin
              register_file[io_addr[4:0]] <= uio_in;
            end
          endcase
        end else begin
          case (io_addr)
            63: begin
              io_out <= 8'h0;
            end
            62: begin
              io_out <= 8'h0;
            end

            30: io_out <= present_ct[7:0];
            31: io_out <= present_ct[15:8];
            32: io_out <= present_ct[23:16];
            33: io_out <= present_ct[31:24];
            34: io_out <= present_ct[39:32];
            35: io_out <= present_ct[47:40];
            36: io_out <= present_ct[55:48];
            37: io_out <= present_ct[63:56];

            default: begin
              io_out <= register_file[io_addr[4:0]];
            end
          endcase
        end
      end else begin
        if (run_present_next == 1'b1) begin
          run_present_next <= 1'b0;
        end else if (run_sbox_next == 1'b1 && run_sbox == 2'b00) begin
          run_sbox <= 2'b01;
        end else if (run_sbox == 2'b01) begin
          run_sbox_next <= 1'b0;
          run_sbox <= 2'b10;

          register_file[8] <= sbox0_out;
          register_file[9] <= sbox1_out;
          register_file[10] <= sbox2_out;
          register_file[11] <= sbox3_out;
        end else if (run_sbox == 2'b10) begin
          run_sbox <= 2'b00;

          register_file[8] <= sbox0_out;
          register_file[9] <= sbox1_out;
          register_file[10] <= sbox2_out;
          register_file[11] <= sbox3_out;
        end
      end
    end
  end

endmodule
