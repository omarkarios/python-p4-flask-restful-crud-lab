#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db, Plant

app = Flask(__name__)
# Using the standard app.db to match the migration history
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# CORS is essential for the React frontend (Port 4000) to talk to this API (Port 5555)
CORS(app)
migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Plants(Resource):
    def get(self):
        # Fetch all plants and return as a list of dictionaries
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()
        try:
            new_plant = Plant(
                name=data.get('name'),
                image=data.get('image'),
                price=data.get('price'),
                is_in_stock=data.get('is_in_stock', True)
            )
            db.session.add(new_plant)
            db.session.commit()
            return make_response(new_plant.to_dict(), 201)
        except Exception as e:
            return make_response({"errors": [str(e)]}, 400)

class PlantByID(Resource):
    def get(self, id):
        plant = Plant.query.filter_by(id=id).first()
        if not plant:
            return make_response({"error": "Plant not found"}, 404)
        return make_response(plant.to_dict(), 200)

    def patch(self, id):
        plant = Plant.query.filter_by(id=id).first()
        if not plant:
            return make_response({"error": "Plant not found"}, 404)
        
        data = request.get_json()
        # Update only the attributes provided in the request body (like is_in_stock)
        for attr in data:
            if hasattr(plant, attr):
                setattr(plant, attr, data.get(attr))
        
        db.session.commit()
        return make_response(plant.to_dict(), 200)

    def delete(self, id):
        plant = Plant.query.filter_by(id=id).first()
        if not plant:
            return make_response({"error": "Plant not found"}, 404)
        
        db.session.delete(plant)
        db.session.commit()
        
        # Requirement: Return empty string with 204 status code
        return make_response("", 204)

# Registering the routes
api.add_resource(Plants, '/plants')
api.add_resource(PlantByID, '/plants/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)