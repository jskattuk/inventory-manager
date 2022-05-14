init:
	python3 -m venv venv; \
	. venv/bin/activate; \
	pip install -r requirements.txt

run:
	. venv/bin/activate; \
  python3 src/main.py
