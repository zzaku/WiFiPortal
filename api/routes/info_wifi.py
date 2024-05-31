from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

info_wifi_blueprint = Blueprint('info_wifi', __name__)

db_config = {
    'host': "127.0.0.1",
    'user': "root",
    'password': "root",
    'database': "wifi_data",
    'port': 8889
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@info_wifi_blueprint.route('/clients', methods=['GET'])
@jwt_required()
def get_clients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT client_mac_address FROM wifi_logs")
    clients = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([client[0] for client in clients])

@info_wifi_blueprint.route('/client/<client_mac>', methods=['GET'])
@jwt_required()
def get_client_info(client_mac):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Combien de temps connecté
    cursor.execute("SELECT SUM(session_duration) FROM wifi_logs WHERE client_mac_address = %s", (client_mac,))
    total_time = cursor.fetchone()[0] or 0

    # Sur quelles bornes
    cursor.execute("SELECT DISTINCT connected_ap_name FROM wifi_logs WHERE client_mac_address = %s", (client_mac,))
    aps = cursor.fetchall()

    # Volume de données échangées
    cursor.execute("SELECT SUM(upstream_transferred), SUM(downstream_transferred) FROM wifi_logs WHERE client_mac_address = %s", (client_mac,))
    volumes = cursor.fetchone()
    total_upstream = volumes[0] or 0
    total_downstream = volumes[1] or 0

    cursor.close()
    conn.close()

    return jsonify({
        'total_time_connected': total_time,
        'access_points': [ap[0] for ap in aps],
        'total_upstream_transferred': total_upstream,
        'total_downstream_transferred': total_downstream
    })

@info_wifi_blueprint.route('/wifi_volume', methods=['GET'])
@jwt_required()
def wifi_volume():
    return jsonify({"message": "Volume de données échangées pour une borne wifi"}), 200

@info_wifi_blueprint.route('/client_info', methods=['GET'])
@jwt_required()
def client_info():
    return jsonify({"message": "Informations sur un client donné"}), 200

# Route pour le dashboard
@info_wifi_blueprint.route('/dashboard', methods=['GET', 'POST'])
@jwt_required()
def dashboard():
    # Ici, vous récupérerez les données depuis la base de données et retournerez les informations pour le dashboard
    return render_template('dashboard.html')

@info_wifi_blueprint.route('/dashboard_data', methods=['GET'])
@jwt_required()
def dashboard_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(DISTINCT connected_ap_name) FROM wifi_logs")
        num_aps = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT client_mac_address) FROM wifi_logs")
        num_clients = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(upstream_transferred + downstream_transferred) FROM wifi_logs")
        total_volume = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return jsonify({
            "numAPs": num_aps,
            "numClients": num_clients,
            "totalVolume": total_volume
        })

    except mysql.connector.Error as err:
        return jsonify({"error": "impossible de récupérer les données"}), 500
