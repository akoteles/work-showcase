drop table SOURCE_SYSTEM_A_OP.ETL_SOURCES ;

CREATE COLUMN TABLE SOURCE_SYSTEM_A_OP.ETL_SOURCES
( SYSTEM_ID   integer not null,
  PROCESS_NAME varchar(100) not null,
  DB_TYPE  varchar(50),
  SERVER   varchar(100),
  PORT     integer,
  USERNAME varchar(100),
  PWD      varchar(100),
  JDBC_URL varchar(1000),
  OTHER_ATTR    varchar(1000),
  Database_Name varchar(100),
  Schema_Name   varchar(100),
  CR_TIMESTAMP  timestamp default CURRENT_TIMESTAMP,
  PRIMARY KEY (SYSTEM_ID,PROCESS_NAME)
);


drop table SOURCE_SYSTEM_A_OP.ETL_QUERY ;

CREATE COLUMN TABLE SOURCE_SYSTEM_A_OP.ETL_QUERY
( QUERY_ID     integer ,
  SYSTEM_ID   integer not null,
  PROCESS_NAME varchar(100) not null,
  QUERY        varchar(4000),
  QUERY_LOB    CLOB,
  COMPILATION_RULE	varchar(4000),
  CR_TIMESTAMP timestamp default CURRENT_TIMESTAMP,
  PRIMARY KEY (PROCESS_NAME)
);


drop table SOURCE_SYSTEM_A_OP.ETL_CONTENT_MAPPING ;

CREATE COLUMN TABLE SOURCE_SYSTEM_A_OP.ETL_CONTENT_MAPPING
( 	COLUMN_ID   		integer not null,
  	PROCESS_ID   		integer not null,
	Table_Name	 		varchar(100),
	Column_Name	 		varchar(100),
	Content_Description	varchar(1000),
	SACK_Node_Label	    varchar(100),
  	CR_TIMESTAMP 		timestamp default CURRENT_TIMESTAMP,
  PRIMARY KEY (COLUMN_ID,PROCESS_ID)
);


drop table SOURCE_SYSTEM_A_OP.ETL_COMPILATION_RULE ;

CREATE COLUMN TABLE SOURCE_SYSTEM_A_OP.ETL_COMPILATION_RULE
( 	RULE_ID   	     	integer not null,
  	PROCESS_ID   		integer not null,
	SACK_Node_Label	    varchar(100),
	COMPILATION_RULE	varchar(4000),
	Reload_Flag         varchar(1) default 'N',
  	CR_TIMESTAMP 		timestamp default CURRENT_TIMESTAMP,
  PRIMARY KEY (RULE_ID,PROCESS_ID)
);
