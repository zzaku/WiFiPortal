from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

auth_blueprint = Blueprint('auth', __name__)

db_config = {
    'host': "127.0.0.1",
    'user': "root",
    'password': "root",
    'database': "wifi_data",
    'port': 8889
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"message": "Missing username or password"}), 400
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
            conn.commit()
            return jsonify({"message": "User registered successfully"}), 201
        except mysql.connector.Error as err:
            return jsonify({"message": "Failed to register user", "error": str(err)}), 500
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

# Route pour se connecter
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"message": "Missing username or password"}), 400
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result and check_password_hash(result[0], password):
                access_token = create_access_token(identity=username)
                return jsonify(access_token=access_token), 200
            else:
                return jsonify({"message": "Invalid username or password"}), 401
        except mysql.connector.Error as err:
            return jsonify({"message": "Failed to login", "error": str(err)}), 500
        finally:
            cursor.close()
            conn.close()
    return render_template('login.html')

@auth_blueprint.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Deconnexion réussi"}), 200
