{
  description = "Generate a HTML & PDF resume from markdown.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    { flake-parts, ... }@inputs:
    flake-parts.lib.mkFlake { inherit inputs; } {
      # Build for all systems in nixpkgs:
      systems = builtins.attrNames inputs.nixpkgs.legacyPackages;

      imports = [ inputs.treefmt-nix.flakeModule ];

      perSystem =
        { config, pkgs, ... }:
        {
          # The actual package
          packages.default = import ./. { inherit pkgs; };

          treefmt = {
            # File used to find flake root
            projectRootFile = "flake.nix";

            programs = {
              # Nixfmt for nix
              nixfmt-rfc-style.enable = true;
              # Black for python
              black.enable = true;
              # Prettier for stylesheets
              prettier.enable = true;
            };
          };
        };
    };
}
