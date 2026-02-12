# Building Python Packages

We are following the guide from [Python Packages](https://py-pkgs.org/welcome) by Tomas Beuzen and Tiffany Timbers for the structure of this template repo. This readme documents differences from their guide.

## Python Installation

We will use [uv](https://docs.astral.sh/uv/guides/install-python/) instead of [conda](https://anaconda.org/anaconda/conda).

### Installing uv and python

1. Follow [uv's installation scripts](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)
2. Now run `uv python install --default`.

- You can see your available python versions with `uv python list`.
- If you want a specific version of python you can run `uv python install 3.12` for example.
- You can upgrade to the latest supported patch release for each version with `uv python upgrade`

3. Now you can install the two python packages recommended `uv pip install poetry cookiecutter --system`
4. I propose skipping the PyPI setup and the rest of chapter 2 for now.

## In progress notes

- Maybe [stop using poetry and start using uv](https://github.com/mkniewallner/migrate-to-uv) or this [stackoverlow](https://stackoverflow.com/questions/79118841/how-can-i-migrate-from-poetry-to-uv-package-manager). One response recommended [uv-migrator](https://lib.rs/crates/uv-migrator)

1. Also install mkdocs-material with `uv pip install mkdocs-material --system`.
2. You can follow [this video for a guide on mkdocs-material](https://www.youtube.com/watch?v=xlABhbnNrfI). His [companion website for this video](https://jameswillett.dev/getting-started-with-material-for-mkdocs/) will be handy as well.

- However, we are using `uv` and will use `uv run mkdocs new .` instead of `mkdocs new .`

The way to install packages from Github

`uv pip install "git+https://github.com/byuirpytooling/pypackage_template.git@main"`

```bash
uv pip install "git+https://github.com/byuirpytooling/pypackage_template.git@main"
```

## Directory structure

```bash
pypackage_template
├── .readthedocs.yml           ┐
├── CHANGELOG.md               │
├── CONDUCT.md                 │
├── CONTRIBUTING.md            │
├── docs                       │
│   ├── changelog.md           │
│   ├── conduct.md             │
│   ├── conf.py                │
│   ├── contributing.md        │ Package documentation
│   ├── example.ipynb          │
│   ├── index.md               │
│   ├── make.bat               │
│   ├── Makefile               │
│   └── requirements.txt       │
├── LICENSE                    │
├── README.md                  ┘
├── pyproject.toml             ┐
├── src                        │
│   └── pypackage_template     │ Package source code, metadata,
│       ├── __init__.py        │ and build instructions
│       └── pycounts.py        ┘
└── tests                      ┐
    └── test_pycounts.py       ┘ Package tests
```
