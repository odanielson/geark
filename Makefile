


check:
	pyflakes geark
	pep8 geark

test:
	python -m unittest discover geark 'test*.py'

refs/www.gevent.org:
	cd refs && wget --recursive --no-clobber --page-requisites --html-extension --convert-links --restrict-file-names=unix --domains gevent.org --no-parent http://www.gevent.org/contents.html

download_docs: refs/www.gevent.org
