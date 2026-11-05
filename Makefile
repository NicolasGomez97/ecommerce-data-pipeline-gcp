# Atajos para Mac y Linux. En Windows usá directamente: python run.py <comando>
SOURCE ?= auto

.PHONY: setup ingest build run docs dashboard check

setup:
	python run.py setup

ingest:
	python run.py ingest --source $(SOURCE)

build:
	python run.py build

run:
	python run.py run --source $(SOURCE)

docs:
	python run.py docs

dashboard:
	python run.py dashboard

check:
	python run.py check
