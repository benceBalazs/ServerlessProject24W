# HOW TO INSTALL DEV ENVIRONMENT
# Install devenv (https://devenv.sh/getting-started/)
# [OPTIONAL] Install direnv (https://direnv.net/docs/installation.html)
# load environment with `devenv shell`

{ pkgs, lib, config, inputs, ... }:

let
  # define additional packages not available in Nixpkgs here
  customPackages = [
    # build functions_framework package
    (pkgs.python312Packages.buildPythonPackage rec {
      pname = "functions_framework";
      version = "3.8.2";
      src = pkgs.fetchPypi {
        pname = "functions_framework";
        version = "3.8.2";
        sha256 = "109bcdca01244067052a605536b44d042903b3805d093cd32e343ba5affffc90";
      };
    })
  ];
in
{
  # automatically install teraform
  env.TENV_AUTO_INSTALL = true;

  # define packages available in Nixpkgs here
  packages = with pkgs; customPackages ++ [
      git
      tenv                                   # terraform
      # general python
      python312Packages.pip                  # python package manager
      python312Packages.google-cloud-storage # google cloud storage
      python312Packages.google-cloud-pubsub  # google cloud pubsub
  ];

  languages.python = {
    enable = true;
    package = pkgs.python312;
  };

  enterShell = ''
  '';

}
