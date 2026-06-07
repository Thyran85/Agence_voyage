BEGIN
    EXECUTE IMMEDIATE q'[
        ALTER TABLE reservations ADD (status VARCHAR2(20) DEFAULT 'EN ATTENTE' NOT NULL)
    ]';
EXCEPTION
    WHEN OTHERS THEN
        -- ignore "column already exists" error (different Oracle versions may return different codes)
        IF SQLCODE NOT IN (-1430, -1400, -900) THEN
            RAISE;
        END IF;
END;
/

COMMIT;
