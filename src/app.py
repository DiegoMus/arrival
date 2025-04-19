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
                    data.get('fechacancelacion'),  # puede ser null
                    data['varlocobro'],
                    data['valortotal'],
                    data['idcliente'],
                    1,
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
                #cur.execute("SELECT * FROM RESERVA order by IDRESERVA")
                cur.execute("""
                        SELECT
                        R.IDRESERVA,
                        R.FECHA,
                        R.ASIENTOS,
                        R.FECHACANCELA,
                        R.VARLOCOBRO,
                        R.VALORTOTAL,
                        C.NOMBRE,
                        C.APELLIDO,
                        R.IDCLIENTE,
                        R.IDESTADO,
                        R.IDTARJETA,
                        R.IDVUELO,
                        E.DESCRIPCION
                    FROM
                        RESERVA R
                    INNER JOIN
                        CLIENTE C ON R.IDCLIENTE = C.IDCLIENTE
                    INNER JOIN 
                        ESTADO E ON R.IDESTADO = E.IDESTADO 
                    ORDER BY
                        R.IDRESERVA
                """)
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
    nuevo_estado = data.get("idestado")

    if nuevo_estado is None:
        return jsonify({"error": "El campo 'estado' es requerido"}), 400

    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE RESERVA
                    SET IDESTADO = :idestado,
                        FECHACANCELA = SYSDATE
                    WHERE IDRESERVA = :id
                """, {"idestado": nuevo_estado, "id": id})
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



################## # 🔹 pasajeros 
@app.route('/pasajeros', methods=['GET'])
def obtener_personas():
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM PASAJERO")
                columnas = [col[0] for col in cur.description]
                personas = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
        return jsonify(personas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Obtener una persona por ID
@app.route('/pasajero/<int:id>', methods=['GET'])
def obtener_persona(id):
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM PASAJERO WHERE IDRESERVA = :id", {"id": id})
                fila = cur.fetchone()
                if fila:
                    columnas = [col[0] for col in cur.description]
                    return jsonify(dict(zip(columnas, fila)))
                else:
                    return jsonify({"mensaje": "Persona no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/personas', methods=['POST'])
def crear_persona():
    data = request.json
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO PASAJERO (NOMBRE, APELLIDO, DPI, VACUNAS, NACIMIENTO, IDRESERVA)
                    VALUES (:nombre, :apellido, :dpi, :vacunas, SYSDATE, :idreserva)
                """, data)
            conn.commit()
        return jsonify({"mensaje": "Persona creada"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Actualizar persona


#------ iniciación -------- 

@app.route('/')
def index():
    return render_template('index.html')

#------ personas ----------

@app.route('/personas/formulario')
def formulario_personas():
    idreserva = request.args.get('idreserva')
    return render_template('personas.html', idreserva=idreserva)


# 🔸 Iniciar servidor
if __name__ == '__main__':
    app.run(debug=True)
