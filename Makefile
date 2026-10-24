.PHONY: help install install-dev test lint fmt run-dummies scan-local clean

help:
	@echo "install      - install runtime deps"
	@echo "install-dev  - install runtime + dev deps"
	@echo "test         - run pytest"
	@echo "lint         - run ruff + mypy"
	@echo "run-dummies  - start local dummy servers"
	@echo "scan-local   - scan localhost and write report"
	@echo "clean        - remove caches and reports"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest -q

lint:
	ruff check ethscan tests
	mypy ethscan

run-dummies:
	python tests/dummy_servers.py

scan-local:
	python -m ethscan 127.0.0.1 -p 1-1024 --authorized -o reports/local.html

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -f reports/*.html reports/*.json