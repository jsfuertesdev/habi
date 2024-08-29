"""
Module to handle database operations and utilities like reading JSON files.
"""

import mysql.connector
import json
import os
import traceback
from dotenv import load_dotenv
from utils.Logger import Logger

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")


class DatabaseConnection:
    """
    Handles connection to the MySQL database, manages the cursor, and ensures cleanup.
    """

    def __init__(self):
        """
        Initializes the connection to the database using credentials from environment variables.
        Logs success or failure in the process.
        """
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv("HOST"),
                port=os.getenv("PORT"),
                user=os.getenv("USER"),
                password=os.getenv("PASSWORD"),
                database=os.getenv("DATABASE"),
            )
            self.cursor = self.connection.cursor(dictionary=True)
            Logger.add_to_log("info", "Database connection established.")
        except mysql.connector.Error as e:
            Logger.add_to_log("error", str(e))
            Logger.add_to_log("error", traceback.format_exc())
            Logger.add_to_log("error", f"Error connecting to database: {e}")
            raise

    def __enter__(self):
        """
        Enters the runtime context related to this object. Returns the cursor.
        """
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the runtime context related to this object, ensuring proper cleanup of resources.
        Closes both the cursor and the database connection.
        """
        self.cursor.close()
        self.connection.close()


def get_properties(filters):
    """
    Retrieves properties from the database based on provided filters.
    Filters can include year, city, and state.

    :param filters: A dictionary of filters to apply to the query.
    :return: List of properties matching the filters.
    """
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

    # Apply filters to the query if provided
    if "year" in filters:
        if filters["year"] != "":
            query += " AND p.year = %s"
            params.append(filters["year"])
    if "city" in filters:
        if filters["city"] != "":
            query += " AND p.city = %s"
            params.append(filters["city"])
    if "state" in filters:
        if filters["state"] != "":
            query += " AND s.name = %s"
            params.append(filters["state"])

    with DatabaseConnection() as cursor:
        try:
            # Execute the query with the provided parameters
            cursor.execute(query, params)
            return cursor.fetchall()
        except mysql.connector.Error as e:
            Logger.add_to_log("error", str(e))
            Logger.add_to_log("error", traceback.format_exc())
            Logger.add_to_log("error", f"Error executing query: {e}")
            raise


def read_json(file_path):
    """
    Reads a JSON file and returns its content.

    :param file_path: The path to the JSON file.
    :return: The parsed JSON content as a dictionary.
    """
    try:
        Logger.add_to_log("info", f"Reading JSON file: {file_path}")
        # Specify encoding to avoid issues on different systems
        with open(file_path, "r") as file:
            data = json.load(file)
        Logger.add_to_log("info", f"File JSON read successfully.")
        return data
    except json.JSONDecodeError as e:
        # Catch specific exception for JSON decoding errors
        Logger.add_to_log("error", f"Error reading JSON file: {e}")
        Logger.add_to_log("error", traceback.format_exc())
    except FileNotFoundError as e:
        # Catch file not found error
        Logger.add_to_log("error", f"File not found: {e}")
        Logger.add_to_log("error", traceback.format_exc())
    except Exception as e:
        # Catch other general exceptions
        Logger.add_to_log("error", f"Unexpected error: {e}")
        Logger.add_to_log("error", traceback.format_exc())
