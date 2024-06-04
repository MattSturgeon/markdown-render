{
  description = "Generate a HTML & PDF resume from markdown.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = {flake-parts, ...} @ inputs:
    flake-parts.lib.mkFlake {inherit inputs;} {
      # Build for all systems in nixpkgs:
      systems = builtins.attrNames inputs.nixpkgs.legacyPackages;

      perSystem = {
        config,
        pkgs,
        ...
      }: {
        formatter = pkgs.alejandra;
        packages.default = import ./. {inherit pkgs;};
      };
    };
}
