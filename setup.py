import os
from setuptools import setup


# Support function to read in README.md as the long_description
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='solr-to-es',
      version='0.2.1',
      description='Export Solr Nodes to Elasticsearch Indexes',
      long_description=read('README.md'),
      long_description_content_type='text/markdown',
      author='Scott Stults',
      author_email='sstults@opensourceconnections.com',
      url='https://github.com/o19s/solr-to-es',
      packages=['solr_to_es'],
      entry_points={
          'console_scripts': [
              'solr-to-es=solr_to_es.__main__:main'
          ]
      },
      install_requires=['elasticsearch>=6.0.0,<7.0.0'],
      license='Apache License, Version 2.0',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Natural Language :: English',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6',
          'Topic :: Utilities'
      ],
      keywords='solr elasticsearch o19s')
