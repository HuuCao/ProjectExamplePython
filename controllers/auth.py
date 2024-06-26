# GET /health_check
import jwt
import os

from flask import Blueprint, request, jsonify, make_response, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

from flask.views import MethodView
from ..models import User
from ..models.base import db
from ..decorator.jwt import token_required

# current_app.config.get("DB_NAME")

auth_bp = Blueprint("auth_bp", __name__)

class AuthAPI(MethodView):

## ====================================== Get All User API ====================================== ##

    @token_required
    def get(self):
        current_user = request.user
        print(current_user.isAdmin)
        if current_user.isAdmin is not True:
            return jsonify({ 'message' : 'Cannot perform that function!' })

        users = User.query.all()
        output = []
        for user in users:
            user_data = {}
            user_data['id'] = user.id
            user_data['username'] = user.username
            user_data['isAdmin'] = user.isAdmin
            user_data['createdAt'] = user.createdAt
            user_data['isActivate'] = user.isActivate
            output.append(user_data)
        # print(output)
        return make_response(jsonify({'users': output}), 201)
## ====================================== Create User API ====================================== ##
    def post(self):
        data = request.get_json()

        if not data['username']:
            return jsonify({ 'message': 'Missing Username!' }), 400
        if not data['password']:
            return jsonify({ 'message': 'Missing Password!' }), 400

        check_user = User.query.filter_by(username = data['username']).first()
 
        if check_user :
            return jsonify({ 'message': 'Username already exists!' })

        hashed_password = generate_password_hash(
            data['password']
        )
        new_user = User(
            username = data['username'],
            password = hashed_password,
            isAdmin = True
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({ 'message': 'New user created!' })

## ====================================== Update User API ====================================== ##

class UpdateAPI(MethodView):
    @token_required
    def put(self, id):
        try:
            data = request.get_json()
            current_user = request.user
            print(current_user)
            if current_user.isAdmin is not True:
                return jsonify({ 'message' : 'Cannot perform that function!' })

            update_user = User\
                .query\
                .get(id)

            username = data['username']
            isAdmin = data['isAdmin']
            isActivate = data['isActivate']  

            update_user.username = username
            update_user.isAdmin = isAdmin
            update_user.isActivate = isActivate

            db.session.commit()
            return jsonify({ 'message': 'Updated successfully!' })
        except Exception as err:
            print("================")
            print(err)
            return jsonify({ 'message': 'Update fail!' })

## ====================================== Login API ====================================== ##
class LoginAPI(MethodView):
    # @isAuthenticated
    def post(self):
        try:
            auth = request.get_json()
            print(auth)
            if not auth or not auth['username'] or not auth['password']:
                # returns 401 if any email or / and password is missing
                return make_response(
                    'Could not verify 1',
                    401,
                    {'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
                )

            user = User.query\
                .filter_by(username = auth['username'])\
                .first()
            print(user)

            if not user:
                # returns 401 if user does not exist
                return make_response(
                    'Could not verify',
                    401,
                    {'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
                )
            if check_password_hash(user.password, auth['password']):
                # generates the JWT Token
                token = jwt.encode({
                    'id': user.id,
                    'exp' : datetime.utcnow() + timedelta(minutes = 45)
                }, os.environ.get("JWT_SECRET_KEY"), "HS256")
                return jsonify({'token' : token})
            return make_response('Could not verify',  401, {'Basic realm' : 'login required'})
        except Exception as err:
            print(err)
            return jsonify({ 'message': 'Login fail!' })

class DeleteAPI(MethodView):
    @token_required
    def delete(self, id):
        try:
            current_user = request.user
            print(current_user)
            if current_user.isAdmin is not True:
                return jsonify({ 'message' : 'You are not an admin. Not allowed to create Part!' }), 400

            delete_user = User\
                .query\
                .get(id)
            
            db.session.delete(delete_user)
            db.session.commit()

            return jsonify({ 'message': 'User deleted successfully!' }), 201

        except Exception as error:
            print(error)
            return jsonify({ 'message': 'Delete Fail!' }), 500

auth_view = AuthAPI.as_view("auth_api")
login_view = LoginAPI.as_view("login_api")
update_view = UpdateAPI.as_view("update_api")
delete_view = DeleteAPI.as_view("delete_api")

auth_bp.add_url_rule(
    "/api/auth", view_func = auth_view, methods=["POST", "GET"]
)
auth_bp.add_url_rule(
    "/api/auth/login", view_func = login_view, methods=["POST"]
)
auth_bp.add_url_rule(
    "/api/auth/<int:id>", view_func = update_view, methods=["PUT"]
)
auth_bp.add_url_rule(
    "/api/auth/<int:id>", view_func = delete_view, methods=["DELETE"]
)
# Node: middleware
# python: decorator