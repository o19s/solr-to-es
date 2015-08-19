from setuptools import setup
try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(name='solr-to-es',
      version='0.1',
      description='Export Solr Nodes to Elasticsearch Indexes',
      long_description=read_md('README.md'),
      author='Joe Lawson',
      author_email='jlawson@o19s.com',
      url='https://github.com/o19s/solr-to-es',
      packages=['solr_to_es'],
      entry_points={
        'console_scripts': [
              'solr-to-es=solr_to_es.__main__:main'
        ]
      },
      install_requires=['elasticsearch>=1.6.0,<2.0',
                        'pysolr>=3.3.2,<4.0'],
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
          'Topic :: Utilities'
            ],
      keywords='solr elasticsearch o19s')
