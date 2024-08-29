import mysql.connector
import json
import os
import traceback
from dotenv import load_dotenv
from utils.Logger import Logger

load_dotenv(dotenv_path='.env')

class DatabaseConnection:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host = os.getenv('HOST'),
                port = os.getenv('PORT'),
                user = os.getenv('USER'),
                password = os.getenv('PASSWORD'),
                database = os.getenv('DATABASE')
            )
            self.cursor = self.connection.cursor(dictionary=True)
            Logger.add_to_log("info", 'Database connection established.')
        except mysql.connector.Error as e:
            Logger.add_to_log("error", str(e))
            Logger.add_to_log("error", traceback.format_exc())
            Logger.add_to_log("error", f'Error connecting to database: {e}')
            raise

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.connection.close()

def get_properties(filters):
    query = """
    SELECT p.address, p.city, s.name as state, p.price, p.description
    FROM property p
    JOIN status_history sh ON p.id = sh.property_id
    JOIN status s ON sh.status_id = s.id
    WHERE s.name IN ('pre_venta', 'en_venta', 'vendido')
    AND sh.update_date = (
        SELECT MAX(update_date)
        FROM status_history
        WHERE property_id = p.id
    )
    """
    params = []

    if 'year' in filters:
        if filters['year'] != '':
            query += " AND p.year = %s"
            params.append(filters['year'])
    if 'city' in filters:
        if filters['city'] != '':
            query += " AND p.city = %s"
            params.append(filters['city'])
    if 'state' in filters:
        if filters['state'] != '':
            query += " AND s.name = %s"
            params.append(filters['state'])

    with DatabaseConnection() as cursor:
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except mysql.connector.Error as e:
            Logger.add_to_log("error", str(e))
            Logger.add_to_log("error", traceback.format_exc())
            Logger.add_to_log("error", f'Error executing query: {e}')
            raise
    
def read_json(file_path):
    try:
        Logger.add_to_log("info", f'Reading JSON file: {file_path}')
        with open(file_path, 'r') as file:
            data = json.load(file)
        Logger.add_to_log("info", f'File JSON read successfully.')
        return data
    except Exception as e:
        Logger.add_to_log("error", str(e))
        Logger.add_to_log("error", traceback.format_exc())