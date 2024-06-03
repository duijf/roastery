{ mkShell
, rye
, pre-commit
}:

mkShell {
  name = "roastery-shell";
  buildInputs = [ rye pre-commit ];
}
