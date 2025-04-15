from flask import Flask, jsonify
import oracledb

app = Flask(__name__)

# Configuración de conexión
USER = "proyecto"
PASSWORD = "proyecto"
HOST = "127.0.0.1"  # ej: "localhost" o IP
PORT = 1521
SERVICE_NAME = "XEPDB1"  # ej: "orclpdb1"

# Crear cadena de conexión tipo "dsn"
dsn = f"{HOST}:{PORT}/{SERVICE_NAME}"

@app.route('/reservas')
def obtener_reservas():
    try:
        # Conectar en modo thin (por defecto)
        connection = oracledb.connect(
            user=USER,
            password=PASSWORD,
            dsn=dsn
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM RESERVA")

        columnas = [col[0] for col in cursor.description]
        filas = cursor.fetchall()
        resultado = [dict(zip(columnas, fila)) for fila in filas]

        cursor.close()
        connection.close()
        return jsonify(resultado)

    except oracledb.DatabaseError as e:
        error = str(e)
        return jsonify({"error": error}), 500

if __name__ == '__main__':
    app.run(debug=True)
