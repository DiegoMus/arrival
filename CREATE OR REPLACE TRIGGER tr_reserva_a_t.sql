CREATE OR REPLACE TRIGGER PROYECTO.tr_reserva_a_transaccion_cancela
AFTER UPDATE ON reserva
FOR EACH ROW
WHEN (
    NEW.VARLOCOBRO > 0 AND
    NEW.FECHACANCELA IS NOT NULL
)
DECLARE
    v_id_transaccion NUMBER;
    v_existe_tarjeta NUMBER;
    v_dias_cancelacion NUMBER;
BEGIN
    -- Verificar que la tarjeta exista
    IF :NEW.idtarjeta IS NOT NULL THEN
        SELECT COUNT(*) INTO v_existe_tarjeta
        FROM tarjeta
        WHERE idtarjeta = :NEW.idtarjeta;

        IF v_existe_tarjeta = 0 THEN
            RAISE_APPLICATION_ERROR(-20002, 'La tarjeta especificada no existe');
        END IF;
    END IF;

    -- Calcular días de diferencia sin consultar la tabla (evita ORA-04091)
    --v_dias_cancelacion := TRUNC(:NEW.FECHACANCELA) - TRUNC(:OLD.FECHA);
    
    -- Insertar reintegro
    SELECT seq_transaccion.NEXTVAL INTO v_id_transaccion FROM dual;
    INSERT INTO transaccion (
        idtransaccion,
        descripcion,
        monto,
        tipo,
        idtarjeta
    ) VALUES (
        v_id_transaccion,
        'Reintegro por cancelación de reserva #' || :NEW.idreserva,
        :NEW.VARLOCOBRO,
        0, -- 0 REPRESENTA REINTEGRO
        :NEW.idtarjeta
    );

    -- Si la cancelación fue tardía, aplicar un cargo adicional

END;