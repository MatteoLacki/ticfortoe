PROJECT_NAME = ticfortoe
install:
	virtualenv ve_ticfortoe
	ve_ticfortoe/bin/pip install IPython
	ve_ticfortoe/bin/pip install -e .
# 	ve_ticfortoe/bin/pip install -e ../paramidiac
upload_test_pypi:
	rm -rf dist || True
	python setup.py sdist
	twine -r testpypi dist/* 
upload_pypi:
	rm -rf dist || True
	python setup.py sdist
	twine upload dist/*
py:
	ve_ticfortoe/bin/ipython
worker:
	ve_ticfortoe/bin/python bin/worker.py ticfortoe
