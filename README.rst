Flask-Restful-Routing
=====================


.. image:: https://travis-ci.org/TwoPiCode/flask-restful-routing.svg
    :target: https://travis-ci.org/TwoPiCode/flask-restful-routing

.. image:: https://img.shields.io/github/issues/TwoPiCode/flask-restful-routing.svg
    :target: https://github.com/twopicode/flask-restful-routing

.. image:: https://img.shields.io/pypi/v/flask-restful-routing.svg
    :target: https://pypi.python.org/pypi/flask-restful-routing/


A utility to allow easier route registration for heavily nested Flask-Restful 
APIs.

Allows declaration of loaders to promote re-use of common argument lookup
code.

Motivation
++++++++++


Installation
++++++++++++

  pip install flask-restful-routing



Sample Usage
++++++++++++

.. code-block:: python

  restful_api = Api(app)
  resources = RouteRoot([
      Route('login', '/login', Login),
      Route('search', '/search', Search),
      Route('document', '/documents', Documents, Document, [
          Route('attachment', '/attachments', Attachments, Attachment)
      ])
  ])
  
  resources.register_routes(restful_api)
