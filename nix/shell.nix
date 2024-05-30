{ mkShell
, rye
}:

mkShell {
  name = "roastery-shell";
  buildInputs = [ rye ];
}
