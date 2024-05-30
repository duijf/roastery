{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }: flake-utils.lib.eachSystem ["aarch64-darwin" "x86_64-linux"] (system:
    let
      inherit (pkgs) lib;
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      # Turn all of the stuff from `nix/` into a package set. This allows
      # us to use the `callPackage` design pattern with everything in there
      # and break up our Nix code into multiple files. The newScope stuff is
      # needed so `nix/a.nix` can have `nix/b.nix` as an input.
      packages = lib.makeScope pkgs.newScope (scope:
        lib.packagesFromDirectoryRecursive {
          callPackage = scope.callPackage;
          directory = ./nix;
        });

      devShells.default = self.outputs.packages.${system}.shell;
    }
  );
}
