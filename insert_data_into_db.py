import mysql.connector
import csv
from datetime import datetime

def convert_date(date_str):
    return datetime.strptime(date_str, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')

def convert_float(num_str):
    num_str = num_str.replace(' ', '').replace(',', '.')
    try:
        return float(num_str)
    except ValueError:
        return 0.0

db_config = {
    'host': "127.0.0.1",
    'user': "root",
    'password': "root",
    'database': "wifi_data",
    'port': 8889
}

conn = mysql.connector.connect(**db_config)

cursor = conn.cursor()

cursor.execute("SHOW TABLES LIKE 'script_execution'")

if cursor.fetchone() is None:
    cursor.execute('''
    CREATE TABLE script_execution (
        id INT AUTO_INCREMENT PRIMARY KEY,
        script_name VARCHAR(255),
        execution_date DATETIME
    )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE,
                password_hash VARCHAR(255)
            )
            ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS wifi_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_associated_time DATETIME,
                session_duration FLOAT,
                client_mac_address VARCHAR(255),
                host_name VARCHAR(255),
                device VARCHAR(255),
                os_type VARCHAR(255),
                upstream_transferred FLOAT,
                downstream_transferred FLOAT,
                connected_ap_name VARCHAR(255)
            )
            ''')

    with open('log_wifi_red_hot.csv', 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            try:
                cursor.execute('''
                            INSERT INTO wifi_logs (
                                session_associated_time, session_duration, client_mac_address, host_name,
                                device, os_type, upstream_transferred, downstream_transferred, connected_ap_name
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                    convert_date(row['Session Associated Time']),
                    convert_float(row['Session Duration']),
                    row['Client MAC Address'],
                    row['Host Name'],
                    row['Device'],
                    row['OS Type'],
                    convert_float(row['Upstream Transferred (Bytes)']),
                    convert_float(row['Downstream Transferred (Bytes)']),
                    row['Connected AP Name']
                ))
            except ValueError as e:
                print(f"Error converting data: {e}, row: {row}")
            except mysql.connector.Error as err:
                print(f"MySQL error: {err}, row: {row}")

    cursor.execute('''
            INSERT INTO script_execution (script_name, execution_date)
            VALUES (%s, %s)
            ''', ('import_wifi_data', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    cursor.close()
    conn.close()
else:
    print("Le script a déjà été exécuté. Arrêt.")
    cursor.close()
    conn.close()

