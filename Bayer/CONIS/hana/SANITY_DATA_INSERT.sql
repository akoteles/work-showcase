Insert into "SOURCE_SYSTEM_A_OP"."DIM_SANITY_CATEGORY"  ("NAME","DESCRIPTION")
Values ('Arithmetic','Contains arithmetic tests (e.g. A < B or A = B)');

Insert into "SOURCE_SYSTEM_A_OP"."DIM_SANITY_CATEGORY"  ("NAME","DESCRIPTION")
Values ('Content','Contains checks that adhere to texts for content or compliance with given rules (e.g. A = Ref.*)');

Insert into "SOURCE_SYSTEM_A_OP"."DIM_SANITY_CATEGORY"  ("NAME","DESCRIPTION")
Values ('NULL','Contains checks for NULL values');

Insert into "SOURCE_SYSTEM_A_OP"."DIM_SANITY_CATEGORY"  ("NAME","DESCRIPTION")
Values ('Date_Chronology','Contains checks that check a value for a chronological sequence (A before B, A after B)');

Insert into "SOURCE_SYSTEM_A_OP"."DIM_SANITY_CATEGORY"  ("NAME","DESCRIPTION")
Values ('Date_Format','Contains checks that check a date format (z.B. yyyy-MM-dd)');

Insert into "SOURCE_SYSTEM_A_OP"."DIM_SANITY_CATEGORY"  ("NAME","DESCRIPTION")
Values ('Type','Contains tests that check compliance with given types (e.g. A = Float(2.0)');

commit;



Insert into "SOURCE_SYSTEM_A_OP"."ETL_SANITY_STRUCTURE"
   (SOURCE_DB_NAME,
	TABLE_NAME    ,
	CATEGORY_FK   ,
	OPERATOR      ,
	COLUMN_1      ,
	EXPRESSION_1  ,
	DESCRIPTION   ,
	CREATED_BY    ,
	START_DATE    )
VALUES
   ('IRDA_CRM_SYSTEM_EC1',
	'CLIENT_TABLE_A',
	1,
	'=',
	'IRDA_SYS_COUNTRY',
	'NO',
	'Check when IRDA_SYS_COUNTRY = NORWAY',
	'PLACEHOLDER_ID',
	current_timestamp );

Insert into "SOURCE_SYSTEM_A_OP"."ETL_SANITY_STRUCTURE"
   (SOURCE_DB_NAME,
	TABLE_NAME    ,
	CATEGORY_FK   ,
	OPERATOR      ,
	COLUMN_1      ,
	COLUMN_2      ,
	DESCRIPTION   ,
	CREATED_BY    ,
	START_DATE    )
VALUES
   ('IRDA_CRM_SYSTEM_EC1',
	'CLIENT_TABLE_A',
	1,
	'=',
	'IRDA_SYS_COUNTRY',
	'BPH_Country__c',
	'Check when IRDA_SYS_COUNTRY = BPH_Country__c',
	'PLACEHOLDER_ID',
	current_timestamp );

Insert into "SOURCE_SYSTEM_A_OP"."ETL_SANITY_STRUCTURE"
   (SOURCE_DB_NAME,
	TABLE_NAME    ,
	CATEGORY_FK   ,
	OPERATOR      ,
	COLUMN_1      ,
	EXPRESSION_1  ,
	DESCRIPTION   ,
	CREATED_BY    ,
	START_DATE    )
VALUES
   ('IRDA_CRM_SYSTEM_EC1',
	'CLIENT_TABLE_A',
	1,
	'<',
	'No_Details_vod__c',
	1,
	'Check when No_Details_vod__c < 1',
	'PLACEHOLDER_ID',
	current_timestamp );


commit;



Insert into "SOURCE_SYSTEM_A_OP"."ETL_SANITY_STRUCTURE"
   (SOURCE_DB_NAME,
	TABLE_NAME    ,
	CATEGORY_FK   ,
	OPERATOR      ,
	COLUMN_1      ,
	DESCRIPTION   ,
	CREATED_BY    ,
	START_DATE    )
VALUES
   ('IRDA_CRM_SYSTEM_EC1',
	'CLIENT_TABLE_A',
	3,
	'IS',
	'VExternal_Id_vod__c',
    'Check if VExternal_Id_vod__c is NULL',
	'PLACEHOLDER_ID',
	current_timestamp );

Insert into "SOURCE_SYSTEM_A_OP"."ETL_SANITY_STRUCTURE"
   (SOURCE_DB_NAME,
	TABLE_NAME    ,
	CATEGORY_FK   ,
	OPERATOR      ,
	COLUMN_1      ,
	DESCRIPTION   ,
	CREATED_BY    ,
	START_DATE    )
VALUES
   ('IRDA_CRM_SYSTEM_EC1',
	'CLIENT_TABLE_A',
	3,
	'IS NOT',
	'VExternal_Id_vod__c',
    'Check if VExternal_Id_vod__c is not NULL',
	'PLACEHOLDER_ID',
	current_timestamp );

commit;



Insert into "SOURCE_SYSTEM_A_OP"."ETL_SANITY_STRUCTURE"
   (SOURCE_DB_NAME,
	TABLE_NAME    ,
	CATEGORY_FK   ,
	OPERATOR      ,
	COLUMN_1      ,
	COLUMN_2      ,
	DESCRIPTION   ,
	CREATED_BY    ,
	START_DATE    )
VALUES
   ('IRDA_CRM_SYSTEM_EC1',
	'CLIENT_TABLE_A',
	4,
	'<',
	'LastModifiedDate',
	'SystemModstamp',
    'Check if LastModifiedDate is smaller than SystemModstamp ',
	'PLACEHOLDER_ID',
	current_timestamp );

Insert into "SOURCE_SYSTEM_A_OP"."ETL_SANITY_STRUCTURE"
   (SOURCE_DB_NAME,
	TABLE_NAME    ,
	CATEGORY_FK   ,
	OPERATOR      ,
	COLUMN_1      ,
	EXPRESSION_1  ,
	DESCRIPTION   ,
	CREATED_BY    ,
	START_DATE    )
VALUES
   ('IRDA_CRM_SYSTEM_EC1',
	'CLIENT_TABLE_A',
	4,
	'>',
	'LastModifiedDate',
	'1900-01-01',
    'Check if LastModifiedDate is greather than User input value ',
	'PLACEHOLDER_ID',
	current_timestamp );

Insert into "SOURCE_SYSTEM_A_OP"."ETL_SANITY_STRUCTURE"
   (SOURCE_DB_NAME,
	TABLE_NAME    ,
	CATEGORY_FK   ,
	OPERATOR      ,
	COLUMN_1      ,
	EXPRESSION_1  ,
	DESCRIPTION   ,
	CREATED_BY    ,
	START_DATE    )
VALUES
   ('IRDA_CRM_SYSTEM_EC1',
	'CLIENT_TABLE_A',
	4,
	'=',
	'LastModifiedDate',
	'2017-11-30',
    'Check if LastModifiedDate equals a User input value',
	'PLACEHOLDER_ID',
	current_timestamp );

commit;



Insert into "SOURCE_SYSTEM_A_OP"."ETL_SANITY_STRUCTURE"
   (SOURCE_DB_NAME,
	TABLE_NAME    ,
	CATEGORY_FK   ,
	COLUMN_1      ,
	EXPRESSION_1  ,
	DESCRIPTION   ,
	CREATED_BY    ,
	START_DATE    )
VALUES
   ('IRDA_CRM_SYSTEM_EC1',
	'CLIENT_TABLE_A',
	5,
	'LastModifiedDate',
	'yyyy-MM-dd',
    'Check if LastModifiedDate is of the following date format: yyyy-mm-dd ',
	'PLACEHOLDER_ID',
	current_timestamp );


commit;



Insert into "SOURCE_SYSTEM_A_OP"."ETL_SANITY_STRUCTURE"
   (SOURCE_DB_NAME,
	TABLE_NAME    ,
	CATEGORY_FK   ,
	OPERATOR      ,
	COLUMN_1      ,
	EXPRESSION_1  ,
	DESCRIPTION   ,
	CREATED_BY    ,
	START_DATE    )
VALUES
   ('IRDA_CRM_SYSTEM_EC1',
	'CLIENT_TABLE_A',
	2,
	'LIKE',
	'Name',
	'DRUG_A',
    'Check if NAME contains value DRUG_A',
	'PLACEHOLDER_ID',
	current_timestamp );


Insert into "SOURCE_SYSTEM_A_OP"."ETL_SANITY_STRUCTURE"
   (SOURCE_DB_NAME,
	TABLE_NAME    ,
	CATEGORY_FK   ,
	OPERATOR      ,
	COLUMN_1      ,
	EXPRESSION_1  ,
	EXPRESSION_2  ,
	DESCRIPTION   ,
	CREATED_BY    ,
	START_DATE    )
VALUES
   ('IRDA_CRM_SYSTEM_EC1',
	'CLIENT_TABLE_A',
	2,
	'IN',
	'BPH_Country__c',
	'SE',
	'NO',
    'Check if BPH_Country__c contains ( SE, NO )',
	'PLACEHOLDER_ID',
	current_timestamp );


commit;



update  "SOURCE_SYSTEM_A_OP"."ETL_SANITY_STRUCTURE"
set sack_node_label = 'RefRawNGSFNordicsAEmail', ACTIVE_FLAG='N';

commit;



SELECT
    ID,
    SOURCE_DB_NAME,
	TABLE_NAME     ,
	CATEGORY_FK   ,
	OPERATOR         ,
    COLUMN_1         ,
    COLUMN_2         ,
	EXPRESSION_1  ,
	EXPRESSION_2  ,
    DESCRIPTION
FROM SOURCE_SYSTEM_A_OP.ETL_SANITY_STRUCTURE
WHERE ACTIVE_FLAG ='Y' and END_DATE > current_timestamp
ORDER BY CATEGORY_FK , ID, SACK_NODE_LABEL


truncate table SOURCE_SYSTEM_A_OP.LOG_SANITY_CHECK

Insert into SOURCE_SYSTEM_A_OP.LOG_SANITY_CHECK
(    SANITY_STRUCTURE_ID,
	 ROW_GUID 		    ,
	 DESCRIPTION 		)
VALUES
(

)

select * from SOURCE_SYSTEM_A_OP.LOG_SANITY_CHECK order by 2 desc

select * from "SOURCE_SYSTEM_A_OP"."DIM_SANITY_CATEGORY"

select * from  "SOURCE_SYSTEM_A_OP"."ETL_SANITY_STRUCTURE" order by 1,4



select sum(run_id)+1 run_id
  from (
		select run_id from SOURCE_SYSTEM_A_OP.LOG_SANITY_CHECK
		union all
		select 0 from dummy
		)

select distinct run_id from SOURCE_SYSTEM_A_OP.LOG_SANITY_CHECK


select sum(run_id) run_id
  from (
		select max(run_id) run_id from SOURCE_SYSTEM_A_OP.LOG_SANITY_CHECK where run_id =1
		union all
		select 0 from dummy
		)


select sum(run_id)+1 run_id
  from (
		select distinct run_id from SOURCE_SYSTEM_A_OP.LOG_SANITY_CHECK
		union all
		select 0 from dummy
		)
