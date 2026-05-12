{
  description = "Flake to support ttsky project";

  outputs = { self, dragnpkgs } @ inputs: dragnpkgs.lib.mkFlake {
    devShells.default =
    {
      lib,
      mkShell,

      verilator,
      iverilog,
      gtkwave,

      python313,
    }: mkShell {
      name = "tt";

      packages = [
        verilator
        gtkwave
        iverilog

        (python313.withPackages (ps: with ps; [
          ipython

          numpy
          scipy
          matplotlib
          pandas
          pyqt6
          pyqt6-sip
          scikit-learn
          networkx
          pycryptodome

          tqdm

          yosys

          cocotb
          pytest
        ]))
      ];

      shellHook = ''
      '';
    };
  };
}
