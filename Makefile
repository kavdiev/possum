all: doc

doc:
	cd doc && make html

uml:
	tools/uml.py

model:
	./manage.py graph_models --output=doc/images/models-base.png -g base

