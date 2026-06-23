CREATE TABLE CLIENT_ETL_LOG
(
  LOG_ID          NUMBER,
  LOG_TIMESTAMP   DATE,
  PROCEDURE_NAME  VARCHAR2(200 BYTE),
  LOCATION_TAG    VARCHAR2(200 BYTE),
  LOG_TEXT        CLOB,
  LOG_SHORT_TEXT  VARCHAR2(256 BYTE),
  FAILURE         VARCHAR2(1 BYTE)              DEFAULT 'N'
)
LOB (LOG_TEXT) STORE AS ( ENABLE      STORAGE IN ROW
                          CHUNK       8192
                          RETENTION
                          NOCACHE
                          LOGGING
                        )
LOGGING
NOCOMPRESS
NOCACHE
NOPARALLEL
MONITORING;


COMMENT ON COLUMN CLIENT_ETL_LOG.PROCEDURE_NAME 	IS 'PACKAGE or PROCEDURE which is executing';
COMMENT ON COLUMN CLIENT_ETL_LOG.LOCATION_TAG 	IS 'Location inside the PKG/PRC/Block used to debug a failure or to monitor job progression';
COMMENT ON COLUMN CLIENT_ETL_LOG.LOG_TEXT 		IS 'CLOB datatype used to store the log / error message';
COMMENT ON COLUMN CLIENT_ETL_LOG.LOG_SHORT_TEXT 	IS 'Substring value to 256 length of LOG_TEXT, easier to read and handle';
COMMENT ON COLUMN CLIENT_ETL_LOG.FAILURE 			IS 'Failure flag, Y means a failure was encountered';


CREATE SEQUENCE CLIENT_ETL_LOG_SEQ
  START WITH 1001
  MAXVALUE 9999999999999999
  MINVALUE 1
  CYCLE
  CACHE 5
  NOORDER;
