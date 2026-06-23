CREATE OR REPLACE PROCEDURE SOURCE_B.prc_log
     (   pi_procedure_name    IN VARCHAR2
        ,pi_loc_tag           IN VARCHAR2
        ,pi_log_text          IN CLOB
        ,pi_failure           IN VARCHAR2 default 'N'
     )
IS PRAGMA AUTONOMOUS_TRANSACTION;

BEGIN
    INSERT /*+ append */
      INTO SOURCE_B.T_LOG
              ( LOG_ID,
                LOG_TIMESTAMP,
                PROCEDURE_NAME,
                LOCATION_TAG,
                LOG_TEXT,
                LOG_SHORT_TEXT,
                FAILURE)
         VALUES
              ( SOURCE_B.SEQ_T_LOG_ID.NEXTVAL,
                SYSDATE,
                pi_procedure_name,
                pi_loc_tag,
                pi_log_text,
                substr(pi_log_text,1,256),
                pi_failure);
    COMMIT;

EXCEPTION
   WHEN OTHERS
   THEN
    RAISE;
END prc_log;
