CREATE OR REPLACE TRIGGER tr_reserva_a_transaccion_mejorado
AFTER INSERT ON reserva
FOR EACH ROW
WHEN (NEW.VARLOCOBRO> 0)  -- Solo ejecutar si el monto es positivo
DECLARE
    v_id_transaccion NUMBER;
    v_existe_tarjeta NUMBER;
    v_existe_boleto NUMBER;
BEGIN
    -- Verificar que exista la tarjeta (si se proporcionó)
    IF :NEW.idtarjeta IS NOT NULL THEN
        SELECT COUNT(*) INTO v_existe_tarjeta FROM tarjeta WHERE idtarjeta = :NEW.idtarjeta;
        IF v_existe_tarjeta = 0 THEN
            RAISE_APPLICATION_ERROR(-20002, 'La tarjeta especificada no existe');
        END IF;
    END IF;
    
    -- Verificar que exista el boleto (si se proporcionó)
    IF :NEW.idboleto IS NOT NULL THEN
        SELECT COUNT(*) INTO v_existe_boleto FROM boleto WHERE idboleto = :NEW.idboleto;
        IF v_existe_boleto = 0 THEN
            RAISE_APPLICATION_ERROR(-20003, 'El boleto especificado no existe');
        END IF;
    END IF;
    
    -- Obtener el próximo ID de transacción usando secuencia (recomendado)
    SELECT seq_transaccion.NEXTVAL INTO v_id_transaccion FROM dual;
    
    -- Insertar en TRANSACCION con más detalles
    INSERT INTO transaccion (
        idtransaccion,
        descripcion,
        monto,
        tipo,
        idtarjeta,
        idboleto,
        usuario_creacion
    ) VALUES (
        v_id_transaccion,
        'Reserva #' || :NEW.idreserva || ' - ' || :NEW.descripcion_reserva,  -- Asumo campo descripción
        :NEW.monto,
        1,  -- Tipo 1 para pagos de reserva
        :NEW.idtarjeta,
        :NEW.idboleto,
        :NEW.idreserva,
        SYSDATE,
        USER
    );
    
    -- Actualizar la reserva con el ID de transacción si hay un campo para ello
    -- UPDATE reserva SET idtransaccion = v_id_transaccion WHERE idreserva = :NEW.idreserva;
    
EXCEPTION
    WHEN OTHERS THEN
        -- Registrar error detallado
        INSERT INTO errores_log (codigo_error, mensaje, fecha, proceso, id_reserva)
        VALUES (SQLCODE, SQLERRM, SYSDATE, 'TRIGGER_TRANSACCION', :NEW.idreserva);
        
        -- Relanzar error modificado
        RAISE_APPLICATION_ERROR(-20001, 'Error al generar transacción. ' || SUBSTR(SQLERRM, 1, 200));
END;