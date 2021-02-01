from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_mail import Message, Mail

from models.user import User
from models.planets import Planet
from models.helpers.planet_march import planet_schema, planets_schema
from models.helpers.user_march import user_schema, users_schema

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

jwt = JWTManager(app)
mail = Mail(app)

@app.route('/planets', methods=["GET"])
def url():
    planet_list = Planet.query.all()
    result = planets_schema.dump(planet_list)
    return jsonify(result)

@app.route('/register', methods=["POST"])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify({"message": "That email already exists."}), 409 #conflit
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        user.save_to_db()
        return jsonify(message="User successfully created"), 201
    
@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login succeded", access_token=access_token), 200
    else:
        return jsonify(message="Bad email or Password"), 401

@app.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("your planetory Api password is " + user.password,
                      sender="admin@planetary-api.com",
                      recipients=[email])
        mail.send(msg)
        return jsonify(message="Password sent to " + email), 200
    else:
        return jsonify(message="That email doesnt exist"), 401
    
@app.route('/planet_details/<int:planet_id>', methods=['GET'])
def planet_details(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result), 200
    else:
        return jsonify(message="That planet does not exist"), 404
    
@app.route('/add_planet', methods=['POST'])
@jwt_required
def add_planet():
    planet_name = request.form['planet_name']
    test = Planet.query.filter_by(planet_name=planet_name).first()
    if test:
        return jsonify("There is already a planet by that name"), 409
    else:
        planet_type = request.form['planet_type']
        home_star = request.form['home_star']
        mass = float(request.form['mass'])
        radius = float(request.form['radius'])
        distance = float(request.form['distance'])
        
        new_planet = Planet(
            planet_name=planet_name,
            planet_type=planet_type,
            home_star=home_star,
            mass=mass,
            radius=radius,
            distance=distance
        )
        db.session.add(new_planet)
        db.session.commit()
        return jsonify(message="You added a planet"), 201

@app.route('/update_planet', methods=['PUT'])
def update_planet():
    planet_id = int(request.form['planet_id'])
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        planet.planet_name = request.form['planet_name']
        planet.planet_type = request.form['planet_type']
        planet.home_star = request.form['home_star']
        planet.mass = float(request.form['mass'])
        planet.radius = float(request.form['radius'])
        planet.distance = float(request.form['distance'])
        db.session.commit()
        return jsonify(message="You updated a planet"), 202
    else:
        return jsonify(message="That planet does not exists"), 404
    
@app.route('/remove_planet/<int:planet_id>)', methods=['DELETE'])
def remove_planet(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message="You deleted a planet"), 404
    else:
        return jsonify(message="You deleted a Planet")


if __name__ == "__main__":
    app.run(debug=True)
