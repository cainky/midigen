# Contributing to MidiGen

Thank you for your interest in contributing to MidiGen! Whether it's reporting bugs, discussing improvements, proposing new features, or writing and reviewing code, your contributions are welcome.

## Getting Started

- Fork the repository on GitHub.
- Clone your forked repository to your local machine.
- Set up your environment with [uv](https://docs.astral.sh/uv/) and make sure that the tests pass:

```bash
uv sync
uv run pytest
```

## Reporting Issues

- Check that the issue has not already been reported.
- Check that the issue has not already been fixed in the latest code.
- Be clear, concise and precise in your description of the problem.
- Open an issue with a descriptive title and a summary in grammatically correct, complete sentences.

## Code Contributions

Here is a quick guide on how to contribute code:

1. Fork the project and clone your fork.
2. Create a new branch for your feature or bugfix.
3. Commit your changes in logical units.
4. Make sure your commit messages are well formatted.
5. Push your changes to a branch in your fork of the repository.
6. Open a pull request, and describe the changes as clearly as possible.

### Code Style

Please adhere to the coding conventions used throughout the project. In particular:

- Use proper variable naming conventions.
- Comment your code where necessary.
- Format with black and keep flake8 clean (CI checks both):

```bash
uv run flake8 midigen example.py
uv run --with black==23.3.0 black midigen example.py
```

Or run every check before committing with `uv run pre-commit run --all-files`.

### Tests and docs

- Bug fixes should come with a test that fails without the fix (see `midigen/tests/test_regressions.py`).
- The Python examples in `README.md` and `index.html`, and `example.py`, are run by `midigen/tests/test_docs.py`, so update them when you change the API.
- `midigen/tests/golden_files/` holds reference MIDI files compared byte for byte. If a change to the output is intended, regenerate them with `REGENERATE_GOLDEN=1 uv run pytest midigen/tests/test_golden_master.py`, check the new files, and commit them.

## Pull Requests

- PRs are welcome! If you see something that could be improved, a new feature that you think would be useful, or a bug you think you can fix, we would love to review your contributions.
- Please make sure that your PR includes tests and your changes don't break the existing tests.
- Please ensure you have merged the latest changes from the main branch before creating your PR.
