setup:
	@echo "Creating virtual environment"
	python -m venv .venv
	powershell -noexit -executionpolicy bypass .venv/Scripts/activate.ps1

install:
	@echo "Installing pip, setuptools, wheel"
	python -m pip install --upgrade pip setuptools wheel

activate:
	powershell -noexit -executionpolicy bypass .venv/Scripts/activate.ps1