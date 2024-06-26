from flask import Blueprint, request, jsonify, make_response, current_app
from datetime import datetime, timedelta

from flask.views import MethodView
from ..models import Part
from ..models.base import db
from ..decorator.jwt import token_required

# current_app.config.get("DB_NAME")

part_bp = Blueprint("part_bp", __name__)

class PartAPI(MethodView):
    @token_required
    def get(self):
        current_user = request.user
        print(current_user.isAdmin)
        if current_user.isAdmin is not True:
            return jsonify({ 'message' : 'Cannot perform that function!' })
            
        part_type = request.args.get('type')
        name = request.args.get('name')
        search = "%{}%".format(name or '')
        
        if part_type is not None:
            parts = Part.query.filter(Part.isActivate.is_(True), Part.type.ilike(part_type), Part.name.ilike(search)).all()
        else:
            parts = Part.query.filter(Part.isActivate.is_(True), Part.name.ilike(search)).all()
       
        output = []
        print(parts)
        for part in parts:
            part_data = {}
            part_data['id'] = part.id
            part_data['name'] = part.name
            part_data['type'] = part.type
            part_data['price'] = part.price
            part_data['createdAt'] = part.createdAt
            part_data['isActivate'] = part.isActivate
            output.append(part_data)
        # print(output)
        return make_response(jsonify({'parts': output}), 200)
        
    @token_required
    def post (self):
        try:
            data = request.get_json()

            current_user = request.user
            print(current_user)
            if current_user.isAdmin is not True:
                return jsonify({ 'message' : 'You are not an admin. Not allowed to create Part!' })

            if not data['name']:
                return jsonify({ 'message': 'Missing Name!' }), 400
            if not data['type']:
                return jsonify({ 'message': 'Missing Type!' }), 400
            if not data['price']:
                return jsonify({ 'message': 'Missing Price!' }), 400
            
            if data['type'] not in ['cpu', 'ram', 'gpu', 'storage', 'psu', 'case']:
                return jsonify({ 'message': 'Invalid type!' })   
            
            check_part = Part.query.filter_by(name = data['name']).first()

            if check_part:
                return jsonify({ 'message': 'Name already exists!' }), 400

            new_part = Part(
                name = data['name'],
                type = data['type'],
                price = data['price'],
                isActivate = True
            )

            db.session.add(new_part)
            db.session.commit()

            return jsonify({ 'message': 'Part created successfully!' }), 201

        except Exception as error:
            print(error)
            return jsonify({ 'message': 'Create Fail!' }), 500

class GetPartByIdAPI(MethodView):
    @token_required
    def get(self, id):
        current_user = request.user
        print(current_user.isAdmin)
        if current_user.isAdmin is not True:
            return jsonify({ 'message' : 'Cannot perform that function!' })

        part = Part.query.filter_by(id=id).first()

        if not part:
            return jsonify({ 'message': 'Part not found!' }), 400

        part_data = {}
        part_data['id'] = part.id
        part_data['name'] = part.name
        part_data['type'] = part.type
        part_data['price'] = part.price
        part_data['createdAt'] = part.createdAt
        part_data['isActivate'] = part.isActivate
            # output.append(part_data)
        # print(output)
        return make_response(jsonify({'parts': part_data}), 201)

class DeleteAPI(MethodView):
    @token_required
    def delete(self, id):
        try:
            current_user = request.user
            print(current_user)
            if current_user.isAdmin is not True:
                return jsonify({ 'message' : 'You are not an admin. Not allowed to create Part!' }), 400

            delete_part = Part\
                .query\
                .get(id)
            
            db.session.delete(delete_part)
            db.session.commit()

            return jsonify({ 'message': 'Part deleted successfully!' }), 201

        except Exception as error:
            print(error)
            return jsonify({ 'message': 'Delete Fail!' }), 500

class UpdateAPI(MethodView):
    @token_required
    def put(self, id):
        try:
            data = request.get_json()
            current_user = request.user
            print(current_user)
            if current_user.isAdmin is not True:
                return jsonify({ 'message' : 'Cannot perform that function!' })

            update_part = Part\
                .query\
                .get(id)
            data_price = update_part.price
            print(data_price)
            if data['type'] not in ['cpu', 'ram', 'gpu', 'storage', 'psu', 'case']:
                return jsonify({ 'message': 'Invalid type!' })  

            name = data['name']
            type = data['type']
            price = data['price']
            isActivate = data['isActivate']

            # check_price = Part.query.filter_by(price = price).first()
            if price != update_part.price:
                all_builds = update_part.builds
                changed_price = price - update_part.price
                for build in all_builds:
                    build.price = build.price + changed_price
                
            update_part.name = name
            update_part.type = type
            update_part.price = price
            update_part.isActivate = isActivate

            db.session.commit()
            return jsonify({ 'message': 'Updated successfully!' })

        except Exception as err:
            print("================")
            print(err)
            return jsonify({ 'message': 'Update fail!' })


part_view = PartAPI.as_view("part_api")
get_part_view = GetPartByIdAPI.as_view("gte_part_api")
update_view = UpdateAPI.as_view("update_api")
delete_view = DeleteAPI.as_view("delete_api")

part_bp.add_url_rule(
    "/api/parts", view_func = part_view, methods=["POST", "GET"]
)
part_bp.add_url_rule(
    "/api/parts/<int:id>", view_func = get_part_view, methods=["GET"]
)
part_bp.add_url_rule(
    "/api/parts/<int:id>", view_func = update_view, methods=["PUT"]
)
part_bp.add_url_rule(
    "/api/parts/<int:id>", view_func = delete_view, methods=["DELETE"]
)