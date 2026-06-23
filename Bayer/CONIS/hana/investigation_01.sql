
drop table SOURCE_SYSTEM_A_OP.ETL_CONTENT_MAPPING ;

CREATE COLUMN TABLE SOURCE_SYSTEM_A_OP.ETL_CONTENT_MAPPING
( 	CONTENT_ID   		integer not null,
	COLUMN_ID   		integer not null,
  	PROCESS_ID   		integer not null,
  	PROCESS_NAME 		varchar(100) not null,
	Table_Name	 		varchar(100),
	Column_Name	 		varchar(100),
	Type	     		varchar(100),
	Size	     		varchar(10),
	Pick_List_Bounded	varchar(100),
	Content_Description	varchar(1000),
	Comment				varchar(4000),
	SACK_Node_Label	    varchar(100),
	SACK_Property_Name  varchar(100),
  	CR_TIMESTAMP 		timestamp default CURRENT_TIMESTAMP,
  PRIMARY KEY (CONTENT_ID,COLUMN_ID,PROCESS_ID)
);


  delete from SOURCE_SYSTEM_A_OP.ETL_CONTENT_MAPPING  where PROCESS_ID = 3; commit;


  select * from SOURCE_SYSTEM_A_OP.ETL_SOURCES

   delete from SOURCE_SYSTEM_A_OP.ETL_QUERY  where PROCESS_ID != 3;    commit;

  select * from SOURCE_SYSTEM_A_OP.ETL_QUERY  where QUERY_ID =3 ;


  update SOURCE_SYSTEM_A_OP.ETL_QUERY as t
  set t.QUERY_ID = s.QUERY_ID
  from SOURCE_SYSTEM_A_OP.ETL_QUERY t , ( select max(QUERY_ID)+1 query_id from SOURCE_SYSTEM_A_OP.ETL_QUERY ) as s
  where t.query_id= -1;

  commit;



  update SOURCE_SYSTEM_A_OP.ETL_QUERY as t
    set t.QUERY_ID = s.QUERY_ID
  from SOURCE_SYSTEM_A_OP.ETL_QUERY t , ( select max(QUERY_ID)+1 query_id from SOURCE_SYSTEM_A_OP.ETL_QUERY ) as s
  where t.query_id= -1;

  commit;


 select DB_TYPE, USERNAME, PWD, SERVER, JDBC_URL, DATABASE_NAME, SCHEMA_NAME, q.QUERY
 from source_system_a_op.etl_sources s
inner join source_system_a_op.etl_query q on s.system_id = q.process_id




update  SOURCE_SYSTEM_A_OP.ETL_QUERY
set query_id = 2
where process_name = 'RefRawMccConsent';
commit;



    Select IFNULL (max(query_id), 0) query_id, IFNULL (process_id, 0) process_id
       	      from SOURCE_SYSTEM_A_OP.ETL_QUERY
       	     group by process_id
       	     union all
       	    select 0,0 from dummy
       		 ORDER BY process_id;


			select query_id
		    	  from ( select query_id,process_id from SOURCE_SYSTEM_A_OP.ETL_QUERY
					 union all
					 select -1,0 from dummy )
		    	 where IFNULL (process_id,0) = 3;


		        select IFNULL (max(query_id), 0)   from SOURCE_SYSTEM_A_OP.ETL_QUERY;


    Select IFNULL (max(query_id), 0) query_id, IFNULL (process_id, 0) process_id
		       	      from SOURCE_SYSTEM_A_OP.ETL_QUERY
		       	     Group by process_id
		       	     union all
		       	    select 0,0 from dummy
		       		 ORDER BY 2 desc;


select max(query_id)  from SOURCE_SYSTEM_A_OP.ETL_QUERY where process_name = 'GRAPH_DB_LOCAL';


 truncate table SOURCE_SYSTEM_A_OP.xyz;

truncate table SOURCE_SYSTEM_A_OP.ETL_QUERY;

INSERT INTO  SOURCE_SYSTEM_A_OP.ETL_QUERY
(
  SYSTEM_ID    ,
  PROCESS_NAME  ,
  QUERY         ,
  QUERY_LOB
)
Values
(
  1,
  'GRAPH_DB_LOCAL',
  'MATCH (n) DETACH DELETE n;',
  'MATCH (n) DETACH DELETE n;'
);

COMMIT;



INSERT INTO  SOURCE_SYSTEM_A_OP.ETL_QUERY
(
  SYSTEM_ID    ,
  PROCESS_NAME  ,
  QUERY         ,
  QUERY_LOB
)
Values
(
  1,
  'GRAPH_DB_LOCAL2',
  'MATCH (n) RETURN n LIMIT 1;',
  'MATCH (n) RETURN n LIMIT 1;'
);

COMMIT;


 INSERT INTO  SOURCE_SYSTEM_A_OP.ETL_QUERY
(
  SYSTEM_ID    ,
  PROCESS_NAME  ,
  QUERY         ,
  QUERY_LOB
)
Values
(
  3,
  'IRDA_CRM_SYSTEM_EC1',
  'MATCH (n) RETURN n LIMIT 1;',
  'MATCH (n) RETURN n LIMIT 1;'
);

COMMIT;




SELECT
  SOURCE_SYSTEM_A_OP.ETL_COMPILATION_RULE.RULE_ID,
  SOURCE_SYSTEM_A_OP.ETL_COMPILATION_RULE.SACK_NODE_LABEL,
  SOURCE_SYSTEM_A_OP.ETL_COMPILATION_RULE.COMPILATION_RULE,
  SOURCE_SYSTEM_A_OP.ETL_COMPILATION_RULE.RELOAD_FLAG
FROM SOURCE_SYSTEM_A_OP.ETL_COMPILATION_RULE
WHERE process_id = 3 order by RULE_ID
