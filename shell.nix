# shell.nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    ffmpeg
    python3
    python3Packages.flask
    python3Packages.opencv4
    python3Packages.schedule
    python3Packages.pip
  ];

  shellHook = ''
    echo "Camera server environment ready"
  '';
}
