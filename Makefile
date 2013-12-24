upload: dist
	python setup.py sdist upload

install:
	python setup.py install

test: install
	sh genthemall-example.sh

.PHONY: setversion
setversion:
	sed -i "/__version.\+=.\+'/c __version__ = '$(version)'" genthemall/core.py

.PHONY : clean
clean:
	rm dist genthemall/*~ genthemall/*.pyc *~ *.egg-info build *.cfg out .genthemall -rf
