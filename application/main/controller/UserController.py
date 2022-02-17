# /*
# USER CONTROLLER
# */

import logging
import os

from application.main.dto.UserDto import UserDto
from application.main.service.AuthenticationService import token_authenticate
from application.main.service.UserService import UserService
from application.main.service.AuthService import AuthService
from flask import Flask, current_app, jsonify, make_response, request
from flask_restful import Resource, reqparse
from flask_restplus import Api, Namespace, Resource
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

api = UserDto.api
_user = UserDto.user


@api.route('/register')
class UserController(Resource):
    # method_decorators = ['token_required']

    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(__name__)
        self.user_service = UserService()
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=str,
                            help='Email', required=True)
        parser.add_argument("password", type=str,
                            help='Password', required=True)
        parser.add_argument("username", type=str, help='User name')
        self.req_parser = parser
        super(UserController, self).__init__(*args, **kwargs)

    def get(self):
        """GET USER"""
        auth_token = self.user_service.create_user()
        return "Hello from User" + auth_token

    @api.expect(_user, validate=True)
    def post(self):
        """REGISTER_USER"""
        # The image is retrieved as a file
        args = self.req_parser.parse_args(strict=True)
        try:
            user = self.user_service.register_user(
                args.get('username'), args.get('email'), args.get('password'))
            if user:
                auth_token = user.encode_auth_token(user.id)
                responseObject = {
                    # 'auth_token': auth_token.decode(),
                    'auth_token': auth_token,
                    'token_type': 'Bearer',
                    'sp': user.admin,
                    'username': user.user_name
                }
                return responseObject, 201
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return responseObject, 500


@api.route('/login')
class LoginUserController(Resource):
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(__name__)
        self.user_service = UserService()
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=str,
                            help='User email', required=True)
        parser.add_argument("password", type=str,
                            help='Password', required=True)
        parser.add_argument("username", type=str, help='User name')
        self.req_parser = parser
        super(LoginUserController, self).__init__(*args, **kwargs)

    @api.expect(_user, validate=True)
    def post(self):
        """LOGIN-USER"""
        args = self.req_parser.parse_args(strict=True)
        try:
            user = self.user_service.get_user(args.get('email'))
            if user:
                auth_token = self.user_service.login(
                    user, args.get('password'))

                if auth_token:
                    responseObject = {
                        # 'auth_token': auth_token.decode(),
                        'auth_token': auth_token,
                        'token_type': 'Bearer',
                        'sp': user.admin,
                        'username': user.user_name
                    }
                    return responseObject, 200
                else:
                    responseObject = {
                        'status': 'Unauthorized',
                        'message': 'Invalid login details'
                    }
                    return responseObject, 401
                    # return make_response(jsonify(responseObject)), 401
            else:
                responseObject = {
                    'status': 'Unauthorized',
                    'message': 'Invalid login details : email'
                }
                return responseObject, 401
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return responseObject, 500


@api.route('/logout')
class LogoutAPI(Resource):
    """
    LOGOUT-USER
    """

    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(__name__)
        self.user_service = UserService()
        self.auth_service = AuthService()
        super(LogoutAPI, self).__init__(*args, **kwargs)

    def get(self):
        # get auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            try:
                if(self.user_service.logout(auth_token)):
                    return {
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    }, 200
                else:
                    return {
                        'status': 'fail'
                    }, 500

            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': e
                }
                return responseObject, 500

        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return responseObject, 403
