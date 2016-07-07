import os
from setuptools import setup

readme_path = os.path.join(os.path.dirname(
  os.path.abspath(__file__)),
  'README.rst',
)
long_description = open(readme_path).read()
version_path = os.path.join(os.path.dirname(
  os.path.abspath(__file__)),
  'VERSION',
)
version = open(version_path).read()

setup(
  name='flask-restful-routing',
  version=version,
  py_modules=['flask_restful_routing'],
  author="Nick Whyte",
  author_email='nick@nickwhyte.com',
  description="An easier way to register flask-restful routes",
  long_description=long_description,
  url='https://github.com/twopicode/flask-restful-routing',
  zip_safe=False,
  install_requires=[],
  classifiers=[
    'Intended Audience :: Developers',
    'Programming Language :: Python',
  ],
)
