flask-restful-routing
============================================

Installation
++++++++++++

  pip install marshmallow-sqlalchemy-referential

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
