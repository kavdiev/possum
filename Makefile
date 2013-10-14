DEV=NO
TEST=NO

ifeq ($(TEST),YES)
    SETTINGS = possum.settings_test
endif
ifeq ($(DEV),YES)
    SETTINGS = possum.settings_dev
endif
ifeq ($(DEV),NO)
  ifeq ($(TEST),NO)
    SETTINGS = possum.settings_sample
  endif
endif

all: doc

doc:
	cd doc && make html

uml:
	tools/uml.py
	
launch:
	python manage.py runserver --settings=${SETTINGS}

test:
	python manage.py test --settings=${SETTINGS}
	
model:
	./manage.py graph_models --output=doc/images/models-base.png -g base

