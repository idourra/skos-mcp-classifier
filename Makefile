.PHONY: load run docker-up classify

load:
	python server/skos_loader.py data/taxonomy.jsonld

run:
	uvicorn server.main:app --host 0.0.0.0 --port 8080

classify:
	python client/classify_responses_api.py
