from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
from os import environ
from marshmallow import post_load, fields, ValidationError

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Models
class Game(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    description = db.Column(db.String(255), nullable = False)
    price = db.Column(db.Float, nullable = False)
    inventory_quantity = db.Column(db.Integer)

    def __repr__(self):
        return f'{self.name} {self.description} {self.price} {self.inventory_quantity}'

# Schemas
class GameSchema(ma.Schema):
    id = fields.Integer(primary_key = True)
    name = fields.String(required = True)
    description = fields.String(required = True)
    price = fields.Float(required = True)
    inventory_quantity = fields.Integer()

    class Meta:
        fields = ("id", "name", "description", "price", "inventory_quantity")

    @post_load
    def create_game(self, data, **kwargs):
        return Game(**data)
    
game_schema = GameSchema()
games_schema = GameSchema(many = True)

# Resources
class GameListResource():
    def get(self):
        all_games = Game.query.all()
        return games_schema.dump(all_games), 200
    
    def post(self):
        form_data = request.get_json()
        try:
            new_game = game_schema.load(form_data)
            db.session.add(new_game)
            db.session.commit()
            return game_schema.dump(new_game), 201
        except ValidationError as err:
            return err.messages, 400

class GameResource(Resource):
    def get(self, game_id):
        game_from_db = Game.query.get_or_404(game_id)
        return game_schema.dump(game_from_db)
    
    def delete(self, game_id):
        game_from_db = Game.query.get_orr_404(game_id)
        db.session.delete(game_from_db)
        return "", 204
    
    def put(self, game_id):
        game_from_db = Game.query.get_or_404(game_id)
        if 'name' in request.json:
            game_from_db.name = request.json['name']
        if 'description' in request.json:
            game_from_db.description = request.json['description']
        if 'price' in request.json:
            game_from_db.price = request.json['price']
        if 'inventory_quantity' in request.json:
            game_from_db.inventory_quantity in request.json
        db.session.commit()
        return game_schema.dump(game_from_db)
    
# Routes
api.add_resource(GameListResource, '/api/games')
api.add_resource(GameResource, '/api/games/<int:game_id>')