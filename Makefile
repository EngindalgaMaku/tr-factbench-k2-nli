PYTHON ?= python
export PYTHONPATH := src

.PHONY: validate prepare data-report test compile

validate:
	$(PYTHON) scripts/00_validate_data.py

prepare:
	$(PYTHON) scripts/01_prepare_splits.py
	$(PYTHON) scripts/02_build_atom_annotation_template.py

data-report:
	$(PYTHON) scripts/03_build_data_report.py

test:
	pytest -q

compile:
	$(PYTHON) -m compileall -q src scripts tests
