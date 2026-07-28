.PHONY: install dev lint lint-fix format format-check test test-cov build docs docs-build docs-clean clean pre-commit check-dist

install:
	python -m pip install -e .

dev:
	python -m pip install -e ".[api,requests,dev,docs]"

lint:
	python -m ruff check .
	python -m mypy steplib

lint-fix:
	python -m ruff check . --fix

format:
	python -m ruff format .

format-check:
	python -m ruff format --check .

test:
	python -m pytest

test-cov:
	python -m pytest --cov=steplib --cov-report=term-missing --cov-fail-under=80

build:
	python -m build

docs:
	sphinx-autobuild docs/ docs/_build/html --open-browser

docs-build:
	sphinx-build -b html docs/ docs/_build/html

docs-clean:
	python -c "import shutil; shutil.rmtree('docs/_build', ignore_errors=True)"

pre-commit:
	pre-commit install

check-dist:
	python -m build
	python -m twine check dist/*

clean:
	python -c "import shutil, glob, pathlib; \
		[shutil.rmtree(p, ignore_errors=True) for p in ['build', 'dist', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'htmlcov', 'docs/_build']] + \
		[shutil.rmtree(p, ignore_errors=True) for p in glob.glob('*.egg-info')] + \
		[shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
