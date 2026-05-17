{
  description = "Flake to support ttsky project";

  inputs = {
    self.submodules = true;

    librelane.url = "path:librelane";
  };

  outputs = { self, librelane } @ inputs: let
    nixpkgs = librelane.inputs.nix-eda.inputs.nixpkgs;
    forAllSystems = nixpkgs.lib.genAttrs nixpkgs.lib.systems.flakeExposed;
  in {
    devShells = forAllSystems (system: {
      default = librelane.legacyPackages.${system}.callPackage (
        {
          lib,
          writeShellScriptBin,
          librelane-shell,

          nextpnrWithGui,
          icestorm,
        }: librelane-shell.override {
          extra-packages = [
            (writeShellScriptBin "yowasp-yosys" ''
              exec yosys "$@"
            '')

            nextpnrWithGui
            icestorm
          ];

          extra-python-packages = (ps: with ps; [
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

            cocotb
            pytest

            # tt deps
            cairosvg
            chevron
            gdstk
            gitpython
            mistune
            python-frontmatter
            pyyaml
            requests
            configupdater
          ]);
        }) {};
      });
  };
}
