# Introduction

To distribute the package you need [pandoc](http://pandoc.org) installed and all the python packages in `dev-requirements.txt`.

See https://packaging.python.org/en/latest/distributing.html for more info.

# Packaging and uploading

    python setup.py sdist
    twine upload dist/*
