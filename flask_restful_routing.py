import weakref
import re
import logging
from collections import namedtuple

log = logging.getLogger(__name__)

object_loader = namedtuple('object_loader',
                           ['input_arg', 'output_arg', 'loader'])

__all__ = ['LoaderResponse']


class LoaderResponse(object):
    """
    A response object that can be returned from a loader. If a loader returns
    a LoaderResponse, this response will be directly streamed to the user.

    :param body: The response body
    :param code: The status code of the response
    """
    def __init__(self, body, code=200):
        self._body = body
        self._code = code


def wrapped_cls(cls, loader):
    class Wrapped(cls):
        def __init__(self):
            super(cls, self).__init__()

        def dispatch_request(self, *args, **kwargs):
            # Mutate the kwargs apropriately
            loader_resp = loader(*args, **kwargs)
            if type(loader_resp) == LoaderResponse:
                return loader_resp._body, loader_resp._code

            elif type(loader_resp) == tuple:
                args = loader_resp
                kwargs = {}

            elif type(loader_resp) == dict:
                kwargs = loader_resp

            else:
                args = [loader_resp]
                kwargs = {}

            return super().dispatch_request(*args, **kwargs)

    return Wrapped


class RootRoute(object):
    """
    A root route node.

    :param children: An array of children of this root. Defaults to ``[]``
    """
    def __init__(self, children=None):
        if children is None:
            children = []

        self._children = children

    def register_routes(self, api):
        """Register all children with the given restful-api instance.

        :param api: A ``flask_restful.Api`` instance
        """
        for child in self._children:
            child.register_routes(api, '', '')


class Route(object):
    """Represents a RESTFUL route in an API.

    :param endpoint: The name of the endpoint. Used to generated url
                     arguments. E.g. ``user``. This string must be a singular
                     term. (I.e. not ``users``).
    :param route: The path at which the endpoints are mounted. E.g. ``/users``
    :param plural: A ``flask_restful.Resource`` which is used for plural access
                   (ie, access to ``/users``)
    :param single: The ``flask_restful.Resource`` which is used for single access
                   (ie, access to ``/users/<int:user_id>``)
    :param children: a list of any child routes. (A list of
                     :class:`flask_restful_routing.Route` instances)
    :param single_type: (``str``) The type used to build the route for access
                        to the singular resource. Defaults to ``int``. This type
                        is directly injected into ``@route('/<single_type:param_name>')``
                        when registering this route.
    :param loader: A loader to parse url params provided to the endpoint
                   via the given path.

                   This is a function which accepts all URL arguments for a
                   resource. It's return value will be passed to the method
                   function in the Flask-Restful resource.

                   A loader can alternatively be specified on the
                   singular resource as a method ``restful_loader(url_arg1, ..., url_argn)``.

                   A plural endpoint will inherit the singular parent's
                   loaders if there exists a parent, and a loader was specified.
    """

    def __init__(self, endpoint, route, plural=None, single=None,
                 children=None, single_type='int', loader=None):

        if children is None:
            children = []

        if endpoint.lower().endswith('s'):
            print("Endpoint must be singular.")
            raise ValueError("Endpoints must be singular. Passed endpoint {} "
                             "with route {}".format(endpoint, route))

        self._children = children
        self._endpoint = endpoint
        self._route = route
        self._single = single
        self._plural = plural
        self._single_type = single_type
        self._safe_endpoint = re.sub(r'[^A-Za-z0-9]', '_', self._endpoint)

        self._parent = None

        for child in self._children:
            child._parent = weakref.proxy(self)

        self._loader = loader

        if hasattr(self._single, 'restful_loader'):
            if self._loader is not None:
                raise ValueError("Please specify either "
                                 "`single.restful_loader` or `loader`")
            self._loader = self._single.restful_loader

    @property
    def _plural_endpoint(self):
        if self._endpoint.lower().endswith('y'):
            return self._endpoint[:-1] + 'ies'
        return self._endpoint + 's'

    def register_routes(self, api, endpoint, route):
        single_endpoint = endpoint + self._endpoint
        plural_endpoint = endpoint + self._plural_endpoint
        base_path = route + self._route
        single_path = '{}/<{}:{}_id>'.format(
            base_path,
            self._single_type,
            self._safe_endpoint,
        )

        if self._plural:
            plural_cls = self._plural
            if self._parent is not None and self._parent._loader is not None:
                plural_cls = wrapped_cls(self._plural, self._parent._loader)
                plural_cls.__name__ = plural_endpoint

            api.add_resource(plural_cls, base_path, endpoint=plural_endpoint)
            log.debug("Registered Resource: {} @ {}".format(
                plural_endpoint, base_path))

        if self._single:
            single_cls = self._single
            if self._loader is not None:
                single_cls = wrapped_cls(self._single, self._loader)
                single_cls.__name__ = single_endpoint

            api.add_resource(single_cls, single_path, endpoint=single_endpoint)
            log.debug("Registered Resource: {} @ {}".format(
                single_endpoint, single_path))

        for child in self._children:
            # TODO Wrap children to capture the parent elem
            # child.register_routes(api, )
            child.register_routes(api, plural_endpoint + '-', single_path)
