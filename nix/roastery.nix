{ fava
, python311Packages
}:

let
  pythonDrv =
    { buildPythonPackage
    , toPythonModule
    # Deps
    , beancount
    , hatchling
    , prompt-toolkit
    , rich
    , typer
    }:

    buildPythonPackage {
      name = "roastery";
      src = ../.;
      format = "pyproject";

      nativeBuildInputs = [ hatchling ];
      propagatedBuildInputs = [
        beancount
        rich
        typer
        prompt-toolkit
        (toPythonModule fava)
      ];
    };
in
python311Packages.callPackage pythonDrv {}
