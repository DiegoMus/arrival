from flask import Flask, request, jsonify, render_template, send_from_directory
import oracledb

app = Flask(__name__, static_url_path='/static')

# Configuración de conexión
USER = "proyecto"
PASSWORD = "proyecto"
HOST = "localhost"
PORT = 1521
SERVICE_NAME = "xepdb1"

DSN = f"{HOST}:{PORT}/{SERVICE_NAME}"

@app.route('/styles/<path:filename>')
def styles(filename):
    return send_from_directory('static', filename)

# 🔹 Crear una reserva
@app.route('/reservas', methods=['POST'])
def crear_reserva():
    data = request.json
    print("entro a resrvas post")
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                #cur.execute("""
                 #   INSERT INTO RESERVA (
                  #      FECHA, ASIENTOS, ESTADO, FECHACANCELA,
                   #     VARLOCOBRO, VALORTOTAL, IDCLIENTE,
                    #    IDESTADO, IDTARJETA, IDVUELO
                    #)
                    #VALUES (
                     #   SYSDATE, :asientos, :estado, :fechacancela,
                     #   :varlocobro, :valortotal, :idcliente,
                     #   :idestado, :idtarjeta, :idvuelo
                    #)
                #""", data)

                cur.callproc("CREAR_RESERVA", [
                    None,
                    data['asientos'],
                    data['estado'],
                    data.get('fechacancelacion'),  # puede ser null
                    data['varlocobro'],
                    data['valortotal'],
                    data['idcliente'],
                    data['idestado'],
                    data['idtarjeta'],
                    data['idvuelo']
                ])

            conn.commit()
        return jsonify({"mensaje": "Reserva creada"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Leer todas las reservas
@app.route('/reservas', methods=['GET'])
def obtener_reservas():
    print("entro en reservas")
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM RESERVA")
                columnas = [col[0] for col in cur.description]
                datos = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Leer una reserva por ID
@app.route('/reservas/<int:id>', methods=['GET'])
def obtener_reserva(id):
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM RESERVA WHERE IDRESERVA = :id", {"id": id})
                row = cur.fetchone()
                if row:
                    columnas = [col[0] for col in cur.description]
                    return jsonify(dict(zip(columnas, row)))
                else:
                    return jsonify({"mensaje": "Reserva no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Actualizar una reserva
@app.route('/reservas/<int:id>/estado', methods=['PUT'])
def actualizar_estado_reserva(id):
    data = request.json
    nuevo_estado = data.get("estado")

    if nuevo_estado is None:
        return jsonify({"error": "El campo 'estado' es requerido"}), 400

    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE RESERVA
                    SET ESTADO = :estado
                    WHERE IDRESERVA = :id
                """, {"estado": nuevo_estado, "id": id})
            conn.commit()
        return jsonify({"mensaje": "Estado actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Eliminar una reserva
@app.route('/reservas/<int:id>', methods=['DELETE'])
def eliminar_reserva(id):
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM RESERVA WHERE IDRESERVA = :id", {"id": id})
            conn.commit()
        return jsonify({"mensaje": "Reserva eliminada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def index():
    return render_template('index.html')

# 🔸 Iniciar servidor
if __name__ == '__main__':
    app.run(debug=True)
