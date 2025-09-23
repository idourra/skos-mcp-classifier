.PHONY: load run docker-up classify install server api test export clean clean-exports export-csv export-excel

# Setup commands
install:
	pip install -r server/requirements.txt
	pip install -r client/requirements.txt

# Server commands
load:
	python server/skos_loader.py data/taxonomy.jsonld

server:
	uvicorn server.main:app --host 0.0.0.0 --port 8080

run: server

# API commands  
api:
	python classification_api.py

# Classification commands
classify:
	python client/classify_standard_api.py

test:
	python test_classifier.py

# Export commands
export: export-csv export-excel

export-csv:
	python csv_exporter.py

export-excel:
	python excel_exporter.py

# Cleanup commands
clean-exports:
	python utils/clean_exports.py --execute

clean-exports-dry:
	python utils/clean_exports.py

clean: clean-exports
	rm -f *.log
	rm -f *.tmp
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
