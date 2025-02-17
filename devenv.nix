# HOW TO INSTALL DEV ENVIRONMENT
# Install devenv (https://devenv.sh/getting-started/)
# [OPTIONAL] Install direnv (https://direnv.net/docs/installation.html)
# load environment with `devenv shell`

{ pkgs, lib, config, inputs, ... }:

{
  env.TENV_AUTO_INSTALL = true;

  packages = with pkgs; [
      git
      tenv
  ];

  languages.python.enable = true;

  enterShell = ''
  '';

}
