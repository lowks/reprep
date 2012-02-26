# (common version)
#
.PHONY: all upload compile-website compile website only-upload
	
webdir=website
source=source
autogen=source/api


# also change this in epydoc.cfg
webgit=git --git-dir $(webdir)/.git --work-tree=$(webdir)/ 

all: upload
	
compile-website: website epydoc generate
	PYTHONPATH=`pwd`:$(PYTHONPATH) sphinx-build -W -E -n -a -b html $(source) $(webdir)

generate:
	rm -rf  $(autogen)
	sphinx-autogen -o $(autogen) $(source)/*.rst
	sphinx-apidoc  -o $(autogen) ../src
	 
compile: generate
	PYTHONPATH=`pwd`:$(PYTHONPATH) sphinx-build -E -n -a -b html $(source) $(webdir)
	
website: distclean
	# Check out the website
	git clone $(github_repo) $@
	$(webgit) checkout origin/gh-pages -b gh-pages
	$(webgit) branch -D master

upload: compile-website
	./gitadd.zsh $(webdir)
	$(webgit) push

only-upload: 
		./gitadd.zsh $(webdir)
		$(webgit) push

distclean:
	rm -rf $(webdir)/
	
epydoc:
	epydoc --config epydoc.cfg --introspect-only -v --exclude-introspect=$(package).unittests --debug
