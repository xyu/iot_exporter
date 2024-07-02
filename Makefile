python ?= python3
venv ?= .venv

.PHONY: default clean
.SUFFIXES:
.SECONDARY:

################################################################################
## Special Make Targets
################################################################################

#
# Make without args makes the distribution
#
default: $(venv)

clean:
	rm -rf '$(venv)'
	touch 'requirements.in'

################################################################################
## Physical Targets
################################################################################

#
# Helper for making a Python venv
#
$(venv): requirements.txt
	# Install dependencies based on requirements.txt
	( . $(venv)/bin/activate && pip install --requirement '$<' )
	@touch '$(venv)'
	############################################################
	# Environment Created                                      #
	#                                                          #
	# Please use source to activate it for your shell.         #
	############################################################
	@echo "\n\033[1m\033[34msource $(venv)/bin/activate\033[39m\033[0m\n"
	############################################################

requirements.txt: requirements.in
	# Create the virtual env that we are going to install into
	$(python) -m venv --system-site-packages $(venv)
	# Add pip-tools so we can install and lock
	( . $(venv)/bin/activate && pip install 'pip-tools' )
	# Use pip-tools to generate locked requirements.txt file
	( . $(venv)/bin/activate && pip-compile --strip-extras --generate-hashes --output-file '$@' )
