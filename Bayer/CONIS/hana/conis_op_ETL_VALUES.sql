truncate table SOURCE_SYSTEM_A_OP.ETL_SOURCES;
truncate table SOURCE_SYSTEM_A_OP.ETL_QUERY;

INSERT INTO  SOURCE_SYSTEM_A_OP.ETL_SOURCES
( SYSTEM_ID  ,
  PROCESS_NAME,
  DB_TYPE ,
  SERVER  ,
  PORT    ,
  USERNAME,
  PWD     ,
  JDBC_URL
)
Values
( 1,
  'GRAPH_DB_LOCAL',
  'NEO4J',
  'localhost',
  7687,
  'graph_user',
  'PLACEHOLDER_SECRET',
  'jdbc:neo4j:bolt://localhost:7687'
);

COMMIT;



INSERT INTO  SOURCE_SYSTEM_A_OP.ETL_SOURCES
( SYSTEM_ID  ,
  PROCESS_NAME,
  DB_TYPE ,
  SERVER  ,
  PORT    ,
  USERNAME,
  PWD     ,
  JDBC_URL
)
Values
( 2,
  'SOURCE_SYSTEM_A_OPERATIONAL',
  'HANA',
  'db-hana-01.internal.example.com',
  39015,
  'hana_user',
  'PLACEHOLDER_SECRET',
  'jdbc:sap://db-hana-01.internal.example.com:39015?currentschema=SOURCE_SYSTEM_A_OP'
);

COMMIT;




INSERT INTO  SOURCE_SYSTEM_A_OP.ETL_SOURCES
( SYSTEM_ID  ,
  PROCESS_NAME,
  DB_TYPE ,
  SERVER  ,
  PORT    ,
  USERNAME,
  PWD     ,
  JDBC_URL,
  Database_Name,
  Schema_Name
)
Values
( 3,
  'IRDA_CRM_SYSTEM_EC1',
  'MSSQL',
  'db-mssql-01.internal.example.com',
  51616,
  'oracle_user',
  'PLACEHOLDER_SECRET',
  'useNTLMv2=true;domain=PLACEHOLDER_DOMAIN;Instance=PLACEHOLDER_INSTANCE',
  'IRDA_CRM_SYSTEM_EC1',
  'crm_system'
);

COMMIT;



INSERT INTO  SOURCE_SYSTEM_A_OP.ETL_SOURCES
( SYSTEM_ID  ,
  PROCESS_NAME,
  DB_TYPE ,
  SERVER  ,
  PORT    ,
  USERNAME,
  PWD     ,
  JDBC_URL
)
Values
( 4,
  'LOOKUP_DB',
  'HANA',
  'db-hana-01.internal.example.com',
  39015,
  'hana_user',
  'PLACEHOLDER_SECRET',
  'jdbc:sap://db-hana-01.internal.example.com:39015?currentschema=LOOKUP_CORE'
);

COMMIT;

INSERT INTO  SOURCE_SYSTEM_A_OP.ETL_SOURCES
( SYSTEM_ID  ,
  PROCESS_NAME,
  DB_TYPE ,
  SERVER  ,
  PORT    ,
  USERNAME,
  PWD     ,
  JDBC_URL
)
Values
( 1,
  'GRAPH_DB_SANDBOX',
  'NEO4J',
  'graph-sandbox.internal.example.com',
  7687,
  'graph_user',
  'PLACEHOLDER_SECRET',
  'jdbc:neo4j:bolt://graph-sandbox.internal.example.com:7687'
);

COMMIT;



INSERT INTO  SOURCE_SYSTEM_A_OP.ETL_SOURCES
( SYSTEM_ID  ,
  PROCESS_NAME,
  DB_TYPE ,
  SERVER  ,
  PORT    ,
  USERNAME,
  PWD     ,
  JDBC_URL
)
Values
( 5,
  'GRAPH_DB_PRESANDBOX',
  'NEO4J',
  'localhost',
  7687,
  'graph_user',
  'PLACEHOLDER_SECRET',
  'jdbc:neo4j:bolt://graph-presandbox.internal.example.com:7887'
);

COMMIT;



delete from  SOURCE_SYSTEM_A_OP.ETL_SOURCES
where process_name='GRAPH_DB_PRESANDBOX';
 commit;
