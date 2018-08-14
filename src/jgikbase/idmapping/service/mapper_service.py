from jgikbase.idmapping.builder import IDMappingBuilder
from flask.app import Flask
from flask import request
from jgikbase.idmapping.core.errors import NoTokenError, AuthenticationError,\
    ErrorType, IllegalParameterError, IDMappingError, NoDataException, UnauthorizedError,\
    MissingParameterError
from jgikbase.idmapping.core.user import AuthsourceID, User, Username
from jgikbase.idmapping.core.tokens import Token
from jgikbase.idmapping.core.object_id import NamespaceID, ObjectID
from http.client import responses  # @UnresolvedImport dunno why pydev cries here, it's stdlib
import flask
from typing import List, Tuple, Optional, Set
import traceback
from werkzeug.exceptions import MethodNotAllowed, NotFound
from operator import itemgetter
import json
from json.decoder import JSONDecodeError

# TODO LOG all calls & errors
# TODO ROOT with gitcommit, version, servertime
# TODO CODE try getting rid of src dir and see what happens

# Set up a blueprint later if necessary
# Not sure what's worth doing here for documentation. Swagger at some point ideally.

_APP = 'ID_MAPPER'

_TRUE = 'true'
_FALSE = 'false'


def _format_error(err: Exception, httpcode: int, errtype: ErrorType=None, errprefix: str=''):
    traceback.print_exc()  # TODO LOG remove when logging works
    errjson = {'httpcode': httpcode,
               'httpstatus': responses[httpcode],
               'message': errprefix + str(err)}
    if errtype:
        errjson['appcode'] = errtype.error_code
        errjson['apperror'] = errtype.error_type
    return (flask.jsonify({'error': errjson}), httpcode)
    # TODO LOG log error
    # TODO ERR call id, time


def _get_auth(request, required=True) -> Tuple[Optional[AuthsourceID], Optional[Token]]:
    """
    :returns None if required is False and there is no authorization header.
    :raises NoTokenError: if required is True and there's no authorization header.
    :raises InvalidTokenError: if the authorization header is malformed.
    :raises IllegalParameterError: if the authsource is illegal.
    """
    auth = request.headers.get('Authorization')
    if not auth:
        if required:
            raise NoTokenError()
        return (None, None)
    auth = auth.strip().split()
    if len(auth) != 2:
        raise IllegalParameterError('Expected authsource and token in header.')
    return AuthsourceID(auth[0]), Token(auth[1])


def _users_to_jsonable(users: List[User]) -> List[str]:
    return sorted([u.authsource_id.id + '/' + u.username.name for u in users])


def _objids_to_jsonable(oids: Set[ObjectID]):
    return sorted([{'namespace': o.namespace_id.id, 'id': o.id} for o in oids],
                  key=itemgetter('namespace', 'id'))


def _check_id(id_, name: str) -> str:
    if not isinstance(id_, str):
        raise IllegalParameterError('Expected string for parameter ' + name)
    id_ = id_.strip()
    if not id_:
        raise MissingParameterError(name)
    return id_


def _get_object_ids_from_json(request) -> Tuple[str, str]:
    # flask has a built in get_json() method but the errors it throws suck.
    ids = json.loads(request.data)
    if not isinstance(ids, dict):
        raise IllegalParameterError('Expected JSON mapping in request body')
    admin_id = _check_id(ids.get('admin_id'), 'admin_id')
    other_id = _check_id(ids.get('other_id'), 'other_id ')
    return admin_id, other_id


def create_app(builder: IDMappingBuilder=IDMappingBuilder()):
    """ Create the flask app. """
    app = Flask(__name__)
    app.url_map.strict_slashes = False  # otherwise GET /loc/ won't match GET /loc
    app.config[_APP] = builder.build_id_mapping_system()

    ##########
    # Endpoints
    ##########

    @app.route('/api/v1/namespace/<namespace>', methods=['PUT', 'POST'])
    def create_namespace(namespace):
        """ Create a namespace. """
        authsource, token = _get_auth(request)
        app.config[_APP].create_namespace(authsource, token, NamespaceID(namespace))
        return ('', 204)

    @app.route('/api/v1/namespace/<namespace>/user/<authsource>/<user>', methods=['PUT'])
    def add_user_to_namespace(namespace, authsource, user):
        """ Add a user to a namespace. """
        admin_authsource, token = _get_auth(request)
        app.config[_APP].add_user_to_namespace(admin_authsource, token, NamespaceID(namespace),
                                               User(AuthsourceID(authsource), Username(user)))
        return ('', 204)

    @app.route('/api/v1/namespace/<namespace>/user/<authsource>/<user>', methods=['DELETE'])
    def remove_user_from_namespace(namespace, authsource, user):
        """ Add a user to a namespace. """
        admin_authsource, token = _get_auth(request)
        app.config[_APP].remove_user_from_namespace(
            admin_authsource, token, NamespaceID(namespace),
            User(AuthsourceID(authsource), Username(user)))
        return ('', 204)

    @app.route('/api/v1/namespace/<namespace>/set', methods=['PUT'])
    def set_namespace_params(namespace):
        """ Change settings on a namespace. """
        authsource, token = _get_auth(request)
        pubmap = request.args.get('publicly_mappable')
        if pubmap:  # expand later if more settings are allowed
            if pubmap not in [_TRUE, _FALSE]:
                raise IllegalParameterError(
                    "Expected value of 'true' or 'false' for publicly_mappable")
            app.config[_APP].set_namespace_publicly_mappable(
                authsource, token, NamespaceID(namespace), pubmap == _TRUE)
        return ('', 204)

    @app.route('/api/v1/namespace/<namespace>', methods=['GET'])
    def get_namespace(namespace):
        """ Get a namespace. """
        authsource, token = _get_auth(request, False)
        ns = app.config[_APP].get_namespace(NamespaceID(namespace), authsource, token)
        return flask.jsonify({'namespace': ns.namespace_id.id,
                              'publicly_mappable': ns.is_publicly_mappable,
                              'users': _users_to_jsonable(ns.authed_users)})

    @app.route('/api/v1/namespace', methods=['GET'])
    def get_namespaces():
        public, private = app.config[_APP].get_namespaces()
        return flask.jsonify({'publicly_mappable': sorted([ns.id for ns in public]),
                              'privately_mappable': sorted([ns.id for ns in private])})

    @app.route('/api/v1/mapping/<admin_ns>/<other_ns>', methods=['PUT', 'POST'])
    def create_mapping(admin_ns, other_ns):
        authsource, token = _get_auth(request)
        admin_id, other_id = _get_object_ids_from_json(request)
        app.config[_APP].create_mapping(authsource, token,
                                        ObjectID(NamespaceID(admin_ns), admin_id),
                                        ObjectID(NamespaceID(other_ns), other_id))
        return ('', 204)

    @app.route('/api/v1/mapping/<admin_ns>/<other_ns>', methods=['DELETE'])
    def remove_mapping(admin_ns, other_ns):
        authsource, token = _get_auth(request)
        admin_id, other_id = _get_object_ids_from_json(request)
        app.config[_APP].remove_mapping(authsource, token,
                                        ObjectID(NamespaceID(admin_ns), admin_id),
                                        ObjectID(NamespaceID(other_ns), other_id))
        return ('', 204)

    @app.route('/api/v1/mapping/<ns>/<eyedee>', methods=['GET'])
    def get_mappings(ns, eyedee):
        ns_filter = request.args.get('namespace_filter')
        if ns_filter and ns_filter.strip():
            ns_filter = [NamespaceID(n.strip()) for n in ns_filter.split(',')]
        else:
            ns_filter = []
        admin, other = app.config[_APP].get_mappings(ObjectID(NamespaceID(ns), eyedee), ns_filter)
        return flask.jsonify({'admin': _objids_to_jsonable(admin),
                              'other': _objids_to_jsonable(other)})

    ##################################
    # error handlers
    ##################################

    @app.errorhandler(IDMappingError)
    def general_app_errors(err):
        """ Handle general application errors. These are user-caused and always map to 400. """
        return _format_error(err, 400, err.error_type)

    @app.errorhandler(JSONDecodeError)
    def json_errors(err):
        """ Handle invalid input JSON. """
        return _format_error(err, 400, errprefix='Input JSON decode error: ')

    @app.errorhandler(AuthenticationError)
    def authentication_errors(err):
        """ Handle authentication errors. """
        return _format_error(err, 401, err.error_type)

    @app.errorhandler(UnauthorizedError)
    def authorization_errors(err):
        """ Handle authorization errors. """
        return _format_error(err, 403, err.error_type)

    @app.errorhandler(NoDataException)
    def no_data_errors(err):
        """ Handle requests for data, such as namespaces, that don't exist. """
        return _format_error(err, 404, err.error_type)

    @app.errorhandler(NotFound)
    def not_found_errors(err):
        """ Handle plain old not found errors thrown by Flask. """
        return _format_error(err, 404)

    @app.errorhandler(MethodNotAllowed)
    def method_not_allowed(err):
        """ Handle invalid method requests. """
        return _format_error(err, 405)

    @app.errorhandler(Exception)
    def all_errors(err):
        """ Catch-all error handler of last resort """
        return _format_error(err, 500)

    return app
