CREATE OR REPLACE PROCEDURE verificar_cliente_duplicado (
    p_resultado OUT NUMBER,
    p_mensaje OUT VARCHAR2
)
IS
    v_ultimo_id NUMBER;
    v_count_duplicados NUMBER;
BEGIN
    -- Obtener el último IDCLIENTE
    SELECT MAX(IDCLIENTE) INTO v_ultimo_id FROM CLIENTE;
    
    IF v_ultimo_id IS NULL THEN
        p_resultado := 0;
        p_mensaje := 'La tabla CLIENTE está vacía';
        RETURN;
    END IF;
    
    -- Verificar duplicados
    SELECT COUNT(*) INTO v_count_duplicados
    FROM CLIENTE a
    WHERE EXISTS (
        SELECT 1 FROM CLIENTE b
        WHERE a.IDCLIENTE != b.IDCLIENTE
        AND b.IDCLIENTE = v_ultimo_id
        AND a.NOMBRE = b.NOMBRE
        AND a.APELLIDO = b.APELLIDO
        AND a.TELEFONO = b.TELEFONO
        AND a.DPI = b.DPI
    );
    
    -- Retornar resultados
    IF v_count_duplicados > 0 THEN
        p_resultado := 1;
        p_mensaje := 'El último cliente (ID ' || v_ultimo_id || ') tiene ' || v_count_duplicados || ' duplicados';
    ELSE
        p_resultado := 0;
        p_mensaje := 'El último cliente (ID ' || v_ultimo_id || ') no tiene duplicados';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        p_resultado := -1;
        p_mensaje := 'Error al verificar cliente duplicado: ' || SQLERRM;
END;
/


-----

sql
Copy
CREATE OR REPLACE TRIGGER verificar_duplicados_trigger
AFTER INSERT ON CLIENTE
FOR EACH ROW
DECLARE
    v_resultado NUMBER;
    v_mensaje VARCHAR2(4000);
BEGIN
    verificar_ultimo_registro_repetido(
        'CLIENTE', 'IDCLIENTE', v_resultado, v_mensaje
    );
    -- Puedes registrar el resultado en una tabla de log
    INSERT INTO auditoria_duplicados VALUES(SYSDATE, v_resultado, v_mensaje);
END;


CREATE OR REPLACE PROCEDURE PROYECTO.practica3(p_nom IN VARCHAR2) AS
       CURSOR cur1(pnombre IN VARCHAR2) IS
       SELECT nombre, apellido, dpi
       FROM proyecto.cliente
       WHERE nombre LIKE pnombre || '%';
       cemp_rec cur1%ROWTYPE;
       vnombre VARCHAR2(30);
     BEGIN
       vnombre := p_nom;
       OPEN cur1(vnombre);
       DBMS_OUTPUT.PUT_LINE
         ('Clientes con nombre que comienza con: ' || ' ' || vnombre);
       LOOP
       FETCH cur1 INTO cemp_rec;
	EXIT WHEN cur1%NOTFOUND;
         DBMS_OUTPUT.PUT_LINE
           (cemp_rec.nombre || '  ' || cemp_rec.apellido || '  ' || cemp_rec.dpi);
       END LOOP;
     CLOSE cur1;
     END;
 
