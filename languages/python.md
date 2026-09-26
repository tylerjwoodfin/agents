# Python

- Invoke Python as `python3`.
- Follow the layout this repository already uses (`src/` package, flat module, or scripts). Do not restructure it.
- Put tests where this repository already puts them (`test/` or `tests/`) and use the runner it already uses.
- Add type hints in files that already use them. Do not introduce a typing-only change.
- Configuration and secrets come from Cabinet (`cabinet --get` / `cabinet put`) or the mechanism the repository documents. Do not hard-code them and do not print their values.
- Do not fix imports with `sys.path` edits. Use the install or `PYTHONPATH` approach the README already describes.
