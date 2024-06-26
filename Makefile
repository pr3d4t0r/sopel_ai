# See:  https://raw.githubusercontent.com/pr3d4t0r/sopel_ai/master/LICENSE.txt


SHELL=/bin/bash

BUILD=./build
DEVPI_HOST=$(shell cat devpi-hostname.txt)
DEVPI_PASSWORD=$(shell cat ./devpi-password.txt)
DEVPI_USER=$(shell cat ./devpi-user.txt)
DIST=./dist
MANPAGES=./manpages
PACKAGE=$(shell cat package.txt)
REQUIREMENTS=requirements.txt
API_DOC_DIR="./docs"
VERSION=$(shell echo "from $(PACKAGE) import __VERSION__; print(__VERSION__)" | python)


# Targets:

all: ALWAYS
	make test
	make manpage
	make docs
	make package


clean:
	rm -Rf $(BUILD)/*
	rm -Rf $(DIST)/*
	rm -Rf $(MANPAGES)/*
	rm -Rfv $$(find $(PACKAGE)/ | awk '/__pycache__$$/')
	rm -Rfv $$(find tests | awk '/__pycache__$$/')
	rm -Rfv $$(find . | awk '/.ipynb_checkpoints/')
	rm -Rfv ./.pytest_cache
	mkdir -p ./dist
	pushd ./dist ; pip uninstall -y $(PACKAGE)==$(VERSION) || true ; popd


devpi:
	devpi use $(DEVPI_HOST)
	@devpi login $(DEVPI_USER) --password="$(DEVPI_PASSWORD)"
	devpi use $(DEVPI_USER)/dev
	devpi -v use --set-cfg $(DEVPI_USER)/dev
	@[[ -e "pip.conf-bak" ]] && rm -f "pip.conf-bak"


dockerized: ALWAYS
	make -C "./dockerized" PACKAGE=$(PACKAGE) VERSION=$(VERSION) image
	@echo && docker images | grep "$(PACKAGE)\|REPOSITORY"


dockerpush: ALWAYS
	make -C "./dockerized" PACKAGE=$(PACKAGE) VERSION=$(VERSION) push


docs: ALWAYS
	mkdir -p $(API_DOC_DIR)
	VERSION="$(VERSION)" pdoc --logo="https://images2.imgbox.com/57/94/AsI1WSfy_o.png" --favicon="https://cime.net/upload_area/favicon.ico" -n -o $(API_DOC_DIR) -t ./resources $(PACKAGE)


install:
	pip install -U $(PACKAGE)==$(VERSION)
	pip list | awk 'NR < 3 { print; } /$(PACKAGE)/'


libupdate:
	pip install -U pip
	pip install -Ur $(REQUIREMENTS)


local:
	pip install --no-dependencies -e .


manpage:
	mkdir -p $(MANPAGES)
	t=$$(mktemp) && awk -v "v=$(VERSION)" '/^%/ { $$4 = v; print; next; } { print; }' README.md > "$$t" && cat "$$t" > README.md && rm -f "$$t"
	pandoc --standalone --to man README.md -o $(MANPAGES)/$(PACKAGE).1


nuke: ALWAYS
	make clean


package:
	pip install -r $(REQUIREMENTS)
	python -m build -wn


prune:
	for f in $$(git branch | awk '!/master/ && !/main/ && !/^\*/ { print; }'); do git branch -d "$$f"; done


# The publish: target is for PyPI and Docker Hub, not for the devpi server.
publish:
	twine --no-color check $(DIST)/*
	twine --no-color upload --verbose $(DIST)/*


refresh: ALWAYS
	pip install -U -r requirements.txt


# Delete the Python virtual environment - necessary when updating the
# host's actual Python, e.g. upgrade from 3.7.5 to 3.7.6.
resetpy: ALWAYS
	rm -Rfv ./.Python ./bin ./build ./dist ./include ./lib


targets:
	@printf "Makefile targets:\n\n"
	@cat Makefile| awk '/:/ && !/^#/ && !/targets/ && !/Makefile/ { gsub("ALWAYS", ""); gsub(":", ""); print; } /^ALWAYS/ { next; }'


test: ALWAYS
	@echo "Version = $(VERSION)"
	@make local
	pytest -v ./tests/*.py
	pip uninstall -y $(PACKAGE)==$(VERSION) || true
	rm -Rfv $$(find $(PACKAGE)/ | awk '/__pycache__$$/')
	rm -Rfv $$(find tests | awk '/__pycache__$$/')


tools:
	pip install -Ur dev-tools.txt


upload:
	devpi upload dist/*whl


ALWAYS:

