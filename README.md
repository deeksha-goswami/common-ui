# Hello World Python

A minimal Python project that prints `Hello, world!`.

## Folder Structure

```text
hello-world-python/
├── src/
│   └── hello_world/
│       ├── __init__.py
│       └── app.py
├── tests/
│   └── test_app.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Run

```bash
python -m hello_world.app
```

## Test

```bash
pip install -e ".[dev]"
pytest
```

## Upload To Git

```bash
git init
git add .
git commit -m "Initial hello world Python project"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```
