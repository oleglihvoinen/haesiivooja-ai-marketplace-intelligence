.PHONY: setup data features train test api all

setup:
	python -m pip install -r requirements.txt

data:
	python src/generate_marketplace_data.py

features:
	python src/feature_pipeline.py

train:
	python ml/train_models.py

test:
	PYTHONPATH=. pytest -q

api:
	uvicorn api.main:app --reload

all: data features train test
