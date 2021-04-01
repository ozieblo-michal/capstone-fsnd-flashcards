import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen



AUTH0_DOMAIN = 'solitary-base-2169.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://capstone-fsnd-flashcards.herokuapp.com'

# https://auth0.com/docs/quickstart/backend/python/01-authorization

'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

'''
extracts the access token from the Authorization Header
'''

def get_token_auth_header():

    print(request.headers.get('Authorization', None)

    # attempt to get the header from the request
    auth_header = request.headers.get('Authorization', None)

    # raise an AuthError if no header is present
    if not auth_header:
        raise AuthError({"code": "authorization_header_missing",
                         "description": "Authorization header is needed."},
                        401)

    # attempt to split bearer and the token
    auth_header_splitted = auth_header.split()

    # raise an AuthError if the header is malformed
    if auth_header_splitted[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description": "Authorization header does not start with Bearer."},
                        401)

    if len(auth_header_splitted) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "The header is malformed. Token is not found."
                         },
                        401)

    if len(auth_header_splitted) > 2:
        raise AuthError({"code": "invalid_header",
                         "description": "Authorization header is not Bearer token."
                         },
                        401)

    # return the token part of the header
    token = auth_header_splitted[1]

    return token

'''
checks if the decoded JWT includes the required permission
permission: string permission (i.e. 'post:drink')
payload: decoded jwt payload
'''

def check_permissions(permission, payload):

    if payload.get('permissions'):
        token_permissions = payload.get("permissions")
        # raise an AuthError if the requested permission string is not in the payload permissions array
        if (permission not in token_permissions):
            raise AuthError({'code': 'invalid_permissions',
                             'description': 'User does not have permission'
                             },
                            401)
        else:
            return True
    # raise an AuthError if permissions are not included in the payload
    else:
        raise AuthError({'code': 'invalid_permissions',
                         'description': 'User does not have permissions attached'
                         },
                        401)

'''
validate decoded JWT token and return the decoded payload
token: a json web token (string)
!!NOTE urlopen has a common certificate error described here: 
https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''

def verify_decode_jwt(token):

    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}

    if 'kid' not in unverified_header:
        raise AuthError({'code': 'invalid_header',
                         'description': 'Authorization malformed.'},
                        401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {'kty': key['kty'],
                       'kid': key['kid'],
                       'use': key['use'],
                       'n': key['n'],
                       'e': key['e']}

    if rsa_key:
        try:
            payload = jwt.decode(token,
                                 rsa_key,
                                 algorithms=ALGORITHMS,
                                 audience=API_AUDIENCE,
                                 issuer='https://' + AUTH0_DOMAIN + '/')
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({'code': 'token_expired',
                             'description': 'Token expired.'},
                            401)
        except jwt.JWTClaimsError:
            raise AuthError({'code': 'invalid_claims',
                             'description': 'Incorrect claims. Please, check the audience and issuer.'},
                            401)
        except Exception:
            raise AuthError({'code': 'invalid_header',
                             'description': 'Unable to parse authentication token.'
                             },
                            401)
    raise AuthError({'code': 'invalid_header',
                     'description': 'Unable to find the appropriate key.'
                     },
                    401)

'''
decorator method
permission: string permission
the decorator which passes the decoded payload to the decorated method
'''

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # use the get_token_auth_header method to get the token
            token = get_token_auth_header()

            print(token)

            # use the verify_decode_jwt method to decode the jwt
            payload = verify_decode_jwt(token)
            # use the check_permissions method validate claims and check the requested permission
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator