.DEFAULT_GOAL := format
VENV_DIR = venv

lint:
	isort --check-only --diff .
	find . -name '*.py' -not -path '*/$(VENV_DIR)/*' | xargs pyupgrade --py39-plus
	black --check . --skip-magic-trailing-comma
	flake8

type:
	mypy .

check:
	make lint
	make type

format:
	isort .
	find . -name '*.py' -not -path '*/$(VENV_DIR)/*' | xargs pyupgrade --py39-plus || true
	black . --skip-magic-trailing-comma
