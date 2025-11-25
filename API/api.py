import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env (si existe)
load_dotenv()

app = Flask(__name__)
# Habilitar CORS
CORS(app) 

# Configuración de la Base de Datos usando Variables de Entorno
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

@app.route('/')
def index():
    return jsonify({"mensaje": "API de Estudiantes funcionando correctamente"})

# -------------------------------------------------------------------
# CRUD: READ (Leer todos)
# -------------------------------------------------------------------
@app.route('/estudiantes', methods=['GET'])
def get_estudiantes():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No hay conexión a la base de datos"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estudiantes ORDER BY id DESC")
        result = cursor.fetchall()
        return jsonify(result)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------------------------------------------------
# CRUD: READ ONE (Leer uno por ID)
# -------------------------------------------------------------------
@app.route('/estudiantes/<int:id>', methods=['GET'])
def get_estudiante(id):
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "No DB connection"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estudiantes WHERE id = %s", (id,))
        result = cursor.fetchone()
        if result:
            return jsonify(result)
        return jsonify({"mensaje": "Estudiante no encontrado"}), 404
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------------------------------------------------
# CRUD: CREATE (Crear)
# -------------------------------------------------------------------
@app.route('/estudiantes', methods=['POST'])
def add_estudiante():
    new_student = request.get_json()
    
    if not new_student or 'carnet' not in new_student:
        return jsonify({"error": "Datos incompletos"}), 400

    conn = get_db_connection()
    if conn is None: return jsonify({"error": "No DB connection"}), 500
        
    try:
        cursor = conn.cursor()
        query = "INSERT INTO estudiantes (nombre, apellido, carnet, nota_final) VALUES (%s, %s, %s, %s)"
        values = (new_student['nombre'], new_student['apellido'], new_student['carnet'], new_student['nota_final'])
        cursor.execute(query, values)
        conn.commit()
        
        new_id = cursor.lastrowid
        return jsonify({"mensaje": "Estudiante agregado", "id": new_id}), 201
        
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------------------------------------------------
# CRUD: UPDATE (Actualizar)
# -------------------------------------------------------------------
@app.route('/estudiantes/<int:id>', methods=['PUT'])
def update_estudiante(id):
    updated_data = request.get_json()
    
    if not updated_data:
        return jsonify({"error": "Datos incompletos"}), 400

    conn = get_db_connection()
    if conn is None: return jsonify({"error": "No DB connection"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estudiantes WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"mensaje": "Estudiante no encontrado"}), 404

        query = """
            UPDATE estudiantes 
            SET nombre = %s, apellido = %s, carnet = %s, nota_final = %s 
            WHERE id = %s
        """
        values = (
            updated_data['nombre'], 
            updated_data['apellido'], 
            updated_data['carnet'], 
            updated_data['nota_final'],
            id
        )
        cursor.execute(query, values)
        conn.commit()
        return jsonify({"mensaje": "Estudiante actualizado correctamente"}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------------------------------------------------
# CRUD: DELETE (Eliminar)
# -------------------------------------------------------------------
@app.route('/estudiantes/<int:id>', methods=['DELETE'])
def delete_estudiante(id):
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "No DB connection"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estudiantes WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"mensaje": "Estudiante no encontrado"}), 404

        cursor.execute("DELETE FROM estudiantes WHERE id = %s", (id,))
        conn.commit()
        return jsonify({"mensaje": "Estudiante eliminado correctamente"}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)