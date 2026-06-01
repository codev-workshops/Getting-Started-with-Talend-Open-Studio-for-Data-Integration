.PHONY: setup test validate validate-db clean help

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-18s %s\n", $$1, $$2}'

setup: ## Install dependencies (MySQL, xmllint) and load demo database
	sudo apt-get update -qq
	sudo apt-get install -y -qq mysql-server libxml2-utils
	sudo systemctl start mysql || true
	sudo mysql < DBBackup/demo_db.sql
	@echo "Setup complete."

validate: ## Validate XML, CSV, and SQL file integrity (no DB required)
	python3 scripts/validate.py

validate-db: ## Validate database load and row counts (requires MySQL)
	bash scripts/validate_db.sh

test: validate validate-db ## Run all validations
	@echo "All tests passed."

clean: ## Drop the demo_db database
	sudo mysql -e "DROP DATABASE IF EXISTS demo_db;" || true
