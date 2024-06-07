{ lib, python3Packages }:
python3Packages.buildPythonApplication {
  pname = "markdown-render";
  version = "1.0";
  pyproject = true;

  nativeBuildInputs = [ python3Packages.setuptools-scm ];

  propagatedBuildInputs = with python3Packages; [
    markdown
    weasyprint
  ];

  src = ./.;

  meta = {
    mainProgram = "mdr";
    license = lib.licenses.mit;
  };
}
