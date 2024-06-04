{ lib, python3Packages }:
python3Packages.buildPythonApplication {
  pname = "python-resume";
  version = "1.0";

  propagatedBuildInputs = with python3Packages; [
    markdown
    pyscss
    weasyprint
  ];

  src = ./.;

  meta = {
    mainProgram = "build.py";
    license = lib.licenses.mit;
  };
}
