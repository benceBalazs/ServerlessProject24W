let
  pkgs = import <nixpkgs> {system = "x86_64-linux";};

  functions-framework = {
    buildPythonPackage,
    fetchPypi,
  }:
    buildPythonPackage rec {
      pname = "functions-framework";
      version = "3.8.2";
      src = fetchPypi {
        inherit pname version;
        sha256 = "109bcdca01244067052a605536b44d042903b3805d093cd32e343ba5affffc90";
      };
    };
in
  pkgs.mkShell {
    buildInputs = with pkgs; [
      terraform
      ruff
      (python312.withPackages (ps:
        with ps; [
          cloudevents
          deprecation
          flask
          functions-framework
          google-cloud-monitoring
          google-cloud-pubsub
          google-cloud-storage
          matplotlib
          numpy
          pandas
          pillow
          seaborn
        ]))
    ];
  }
