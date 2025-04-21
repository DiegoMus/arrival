from flask import Flask, request, jsonify, render_template, send_from_directory
from datetime import datetime
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
@app.route('/pasajero/<int:idreserva>', methods=['GET'])
def obtener_persona(idreserva):
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM PASAJERO WHERE IDRESERVA = :id", {"id": idreserva})
                columnas = [col[0] for col in cur.description]
                datos = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
                return jsonify(datos)  # esto ya es una lista
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/personas', methods=['POST'])
def crear_persona():
    data = request.json
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
         
                data["nacimiento"] = datetime.strptime(data["nacimiento"], "%Y-%m-%d %H:%M:%S.%f")
                print("Nacimiento recibido:", data["nacimiento"], type(data["nacimiento"]))


                cur.execute("""
                    INSERT INTO PASAJERO (NOMBRE, APELLIDO, DPI, VACUNAS, NACIMIENTO, IDRESERVA)
                    VALUES (:nombre, :apellido, :dpi, :vacunas, :nacimiento, :idreserva)
                """, data)
            conn.commit()
        return jsonify({"mensaje": "Persona creada"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# INGRESO DE CLIENTE

@app.route('/clientes', methods=['GET'])
def obtener_clientes():
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT IDCLIENTE, NOMBRE, APELLIDO, DPI, TELEFONO FROM CLIENTE")
                clientes = cursor.fetchall()
                resultado = []
                for c in clientes:
                    resultado.append({
                        'IDCLIENTE': c[0],
                        'NOMBRE': c[1],
                        'APELLIDO': c[2],
                        'DPI': c[3], 
                        'TELEFONO': c[4]
                    })
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clientes', methods=['POST'])
def crear_cliente():
    datos = request.get_json()
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO CLIENTE (IDCLIENTE, NOMBRE, APELLIDO, DPI, TELEFONO)
                    VALUES (SEQ_CLIENTE.NEXTVAL, :nombre, :apellido, :dpi, :telefono)
                """, nombre=datos['nombre'], apellido=datos['apellido'], dpi=datos['dpi'], telefono=datos['telefono'])
            conn.commit()
        return jsonify({'mensaje': 'Cliente creado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clientes/<int:id>', methods=['DELETE'])
def eliminar_cliente(id):
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM CLIENTE WHERE IDCLIENTE = :id", id=id)
            conn.commit()
        return jsonify({'mensaje': 'Cliente eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# INGRESO DE TARJETA

@app.route('/tarjeta', methods=['POST'])
def crear_tarjeta():
    data = request.json
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO TARJETA (DESCRIPCION, IDCLIENTE)
                    VALUES (:descripcion, :idcliente)
                """, data)
            conn.commit()
        return jsonify({"mensaje": "Tarjeta registrada"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# LISTAR TARJETAS

@app.route('/tarjetas/<int:idcliente>', methods=['GET'])
def obtener_tarjeta(idcliente):
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM TARJETA WHERE IDCLIENTE = :id", {"id": idcliente})
                columnas = [col[0] for col in cur.description]
                datos = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
                return jsonify(datos)  # esto ya es una lista
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Actualizar persona
@app.route('/personas/<int:id>', methods=['PUT'])
def actualizar_persona(id):
    data = request.json
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE PERSONA
                    SET NOMBRE = :nombre,
                        APELLIDO = :apellido,
                        EDAD = :edad
                    WHERE IDPERSONA = :id
                """, {**data, "id": id})
            conn.commit()
        return jsonify({"mensaje": "Persona actualizada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Eliminar persona
@app.route('/personas/<int:id>', methods=['DELETE'])
def eliminar_persona(id):
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM PASAJERO WHERE IDPASAJERO = :id", {"id": id})
            conn.commit()
        return jsonify({"mensaje": "Persona eliminada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500




#####  Boletos ########

@app.route('/boletos', methods=['POST'])
def crear_boleto():
    try:
        data = request.get_json()
        print("Datos recibidos:", data)  # ✅ debug real, no asignación

        # Validación básica
        campos_requeridos = ['NO_ASIENTO', 'COSTO', 'IDPASAJERO', 'IDVUELO', 'PAIS_ORIGEN', 'PAIS_DESTINO']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({"error": f"Falta el campo requerido: {campo}"}), 400

        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO BOLETO (
                        IDBOLETO,
                        NO_ASIENTO,
                        COSTO,
                        IDPASAJERO,
                        IDVUELO,
                        PAIS_ORIGEN,
                        PAIS_DESTINO
                    ) VALUES (
                        SEQ_BOLETO.NEXTVAL,
                        :no_asiento,
                        :costo,
                        :idpasajero,
                        :idvuelo,
                        :pais_origen,
                        :pais_destino
                    )
                """,
                no_asiento=data['NO_ASIENTO'],
                costo=data['COSTO'],
                idpasajero=data['IDPASAJERO'],
                idvuelo=data['IDVUELO'],
                pais_origen=data['PAIS_ORIGEN'],
                pais_destino=data['PAIS_DESTINO'])

            conn.commit()
            return jsonify({"mensaje": "Boleto creado exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard')
def resumen_pasajeros():
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        v.IDVUELO AS vuelo,
                        COUNT(p.IDPASAJERO) AS numero,
                        p2.NOMBRE AS PAISORIGEN,
                        p3.NOMBRE AS PAISDESTINO

                    FROM PASAJERO p
                    JOIN RESERVA r ON p.IDRESERVA = r.IDRESERVA
                    JOIN VUELO v ON v.IDVUELO = r.IDVUELO
                    JOIN PAIS p2 ON	v.PAIS_ORIGEN = p2.IDPAIS 
                    JOIN PAIS p3 ON v.PAIS_DESTINO =p3.IDPAIS 
                    WHERE r.IDESTADO = 1
                    GROUP BY v.IDVUELO, p2.NOMBRE, p3.NOMBRE 
                """)
                columnas = [col[0] for col in cursor.description]
                resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
                return render_template('dashboard.html', datos=resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

## vuelos

@app.route('/vuelo', methods=['GET'])
def obtener_vuelos():
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM VUELO")
                clientes = cursor.fetchall()
                resultado = []
                for c in clientes:
                    resultado.append({
                        'IDVUELO': c[0],
                        'DESCRIPCION': c[1],
                        'DISPONIBILIDAD': c[2],
                        'IDAVION': c[3],
                        'PAIS_ORIGEN': c[4],
                        'PAIS_DESTINO': c[5],
                        'IDPAIS': c[6],
                        'FECHA_SALIDA': c[7]
                        
                    })
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#------ iniciación -------- 

@app.route('/reserva/formulario')
def index():
    idtarjeta = request.args.get('idtarjeta')
    idvuelo = request.args.get('idvuelo')
    idcliente = request.args.get('idcliente')
    return render_template('index.html', idcliente=idcliente, idtarjeta=idtarjeta, idvuelo=idvuelo)

#------ FRONTEND LOAD ----------

@app.route('/personas/formulario')
def formulario_personas():
    idreserva = request.args.get('idreserva')
    return render_template('personas.html', idreserva=idreserva)

@app.route('/boleto/formulario')
def formulario_boleto():
    idpasajero = request.args.get('idpasajero')
    return render_template('boleto.html', idpasajero=idpasajero)

@app.route('/cliente/formulario')
def formulario_cliente():
    return render_template('cliente.html')

@app.route('/tarjeta/formulario')
def formulario_tarjeta():
    idcliente = request.args.get('idcliente')
    return render_template('tarjeta.html')

@app.route('/vuelo/formulario')
def formulario_vuelo():
    idtarjeta = request
    return render_template('vuelos.html')
    

# 🔸 Iniciar servidor
if __name__ == '__main__':
    app.run(debug=True)
