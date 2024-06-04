{
  description = "Generate a HTML & PDF resume from markdown.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = {nixpkgs, ...}: let
    perSystem = f: builtins.mapAttrs f nixpkgs.legacyPackages;
  in {
    formatter = perSystem (system: pkgs: pkgs.alejandra);
    packages = perSystem (system: pkgs: {
      default = import ./. {inherit pkgs;};
    });
  };
}
