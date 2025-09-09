project = dados-IBGE
subsource = internet

export BRONZE_PATH = ../$(project)/AWS/S3/01.bronze
export SILVER_PATH = ../$(project)/AWS/S3/02.silver
export GOLD_PATH = ../$(project)/AWS/S3/03.gold

export BRONZE_CONFIG = ./assets/bronze.$(subsource).json
export SILVER_CONFIG = ./assets/silver.$(subsource).json
export GOLD_CONFIG = ./assets/gold.$(subsource).json

export AWS_ACCESS_KEY_ID = 
export AWS_SECRET_ACCESS_KEY = 
export AWS_REGION=us-east-1

terraform/init:
	(cd terraform && terraform init)

terraform/plan:
	(cd terraform && terraform plan)

terraform/apply:
	(cd terraform && terraform apply)

terraform/destroy:
	(cd terraform && terraform destroy)

venv:
	python -m venv venv 

venv_requirements:
	venv\Scripts\activate && \
	python.exe -m pip install --upgrade pip && \
	pip install -r requirements.txt 

venv_run:
	venv\Scripts\activate && python src/app.py

## VENV TESTS ##
venv_requirements_tests:
	venv\Scripts\activate && pip install -r requirements-dev.txt 

venv_run_tests:
	venv\Scripts\activate && pytest tests/ingestion_preparation_test.py

## REMOVE VNV ##
venv_remove:
	rmdir /S /Q venv

## LOCAL ##
requirements:
	pip install -r requirements.txt

run: 
	python src/app.py

run_tests:
	pytest tests/ingestion_preparation_test.py

## DOCKER ##


docker_run:
	cd docker && docker run teste

docker_build:
	cd docker && docker build -f Dockerfile -t teste ..

docker_build_compose:
	cd docker && docker-compose up --build

docker_down:
	cd docker && docker-compose down --build

docker_run_airflow:
	cd docker && \
    docker-compose run airflow-worker airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin && \
    docker-compose up

## CPROFILE ##

cprofile_time:
	python -m cProfile -s time src/app.py

cprofile_prof:
	python -m cProfile -o file_profiling.prof src/app.py

## SNAKEVIZ ##

snakeviz:
	snakeviz file_profiling.prof
 
all: venv venv_requirements venv_run