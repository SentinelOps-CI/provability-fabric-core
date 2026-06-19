PYTHON ?= python

.PHONY: pf-core-install pf-core-lean pf-core-schema pf-core-examples pf-core-audit pf-core-unit-tests pf-core-trusted pf-core-e2e pf-core-phase7-smoke

PF_CORE_DIR := pf-core
LEAN_DIR := $(PF_CORE_DIR)/lean
SCHEMAS_DIR := $(PF_CORE_DIR)/schemas
VALIDATOR_DIR := $(CURDIR)/$(PF_CORE_DIR)/validator
PF_CLI := $(PYTHON) -m pf_core.cli core

pf-core-install:
	$(PYTHON) -m pip install -q setuptools wheel jsonschema referencing
	$(PYTHON) -m pip install -q -e $(PF_CORE_DIR)/validator

pf-core-lean:
	cd $(LEAN_DIR) && lake build

pf-core-schema: pf-core-install
	PYTHONPATH=$(VALIDATOR_DIR) $(PF_CLI) schema-check --schemas $(SCHEMAS_DIR)

pf-core-examples: pf-core-install
	PYTHONPATH=$(VALIDATOR_DIR) $(PYTHON) $(PF_CORE_DIR)/scripts/gen_fixtures.py
	PYTHONPATH=$(VALIDATOR_DIR) $(PYTHON) $(PF_CORE_DIR)/scripts/validate_examples.py

pf-core-audit: pf-core-install
	PYTHONPATH=$(VALIDATOR_DIR) $(PF_CLI) audit-boundary --root .

pf-core-unit-tests: pf-core-install
	$(PYTHON) -m pip install -q pytest
	PYTHONPATH=$(VALIDATOR_DIR) $(PYTHON) -m pytest pf-core/validator/tests -q

pf-core-trusted: pf-core-install pf-core-lean pf-core-schema pf-core-examples pf-core-audit pf-core-unit-tests
	@echo "pf-core-trusted: all checks passed"

pf-core-phase7-smoke: pf-core-install pf-core-lean
	PYTHONPATH=$(VALIDATOR_DIR) bash scripts/phase7-cross-repo-smoke.sh

pf-core-e2e: pf-core-install pf-core-lean
	PYTHONPATH=$(VALIDATOR_DIR) bash $(PF_CORE_DIR)/scripts/e2e-replay-gate.sh
