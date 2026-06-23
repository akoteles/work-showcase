SELECT
        t.RULE_ID,
        t.SACK_NODE_LABEL,
        t.COMPILATION_RULE
   FROM SOURCE_SYSTEM_A_OP.ETL_HARMONIZED_COMPILATION_RULE t
  WHERE  RULE_ID = 1
  ORDER BY RULE_ID


  select distinct SACK_NODE_LABEL
  from SOURCE_SYSTEM_A_OP.ETL_CONTENT_MAPPING_1



  select source_query
  from SOURCE_SYSTEM_A_OP.ETL_QUERY_1
  where SACK_NODE_LABEL =


  select column_name
 from source_system_a_op.etl_content_mapping_1
where SACK_NODE_LABEL
order by 1


select *
from SOURCE_SYSTEM_A_OP.ETL_QUERY_1
where SACK_NODE_LABEL


  select *
 from source_system_a_op.etl_content_mapping_1
where SACK_NODE_LABEL = 'RawNGSFNordicsCLM'
order by 1



			  update source_system_a_op.etl_content_mapping_1
			  set column_name = 'Name'
			where SACK_NODE_LABEL = 'RawNGSFNordicsCLM' and column_name = 'Name222';
			commit;


  select *
 from source_system_a_op.etl_content_mapping_1
where SACK_NODE_LABEL = 'RawNGSFNordicsAEmail'
order by 1


		  update source_system_a_op.etl_content_mapping_1
		  set column_name = 'Name'
		where SACK_NODE_LABEL = 'RawNGSFNordicsAEmail' and column_name = 'Name1';
		commit;


		  update source_system_a_op.etl_content_mapping_1
		  set column_name = 'BPH_External_ID__c'
		where SACK_NODE_LABEL = 'RawNGSFNordicsAEmail' and column_name = 'BPH_External_ID__c______111';
		commit;




		SELECT * FROM SOURCE_SYSTEM_A_OP.ETL_HARMONIZED_COMPILATION_RULE t
         WHERE  RULE_ID = 1;



update  SOURCE_SYSTEM_A_OP.ETL_HARMONIZED_COMPILATION_RULE
set compilation_rule = '
MATCH (n:RawNGSFNordicsAEmail)
WITH n AS input, ''#OCB#'' AS VarCreatedBy, ''#OCD#'' AS VarCreatedDate
MATCH (n:RawNGSFNordicsAEmail {IRDA_SYS_OBJECT_GUID:input.IRDA_SYS_OBJECT_GUID})
MATCH (ct:Context {businessArea: ''Pharma''})
MATCH (cxt:Context {country:LEFT(input.BPH_External_ID__c,2)})
MATCH (:Year {opCo18Year: tointeger(substring(input.Capture_Datetime_vod__c, 0, 4))})-[:HAS_MONTH]->(:Month {opCo18Month: tointeger(substring(input.Capture_Datetime_vod__c, 5, 2))})-[:HAS_DAY]->(df:Day {opCo18Day: tointeger(substring(input.Capture_Datetime_vod__c, 8, 2))})
MATCH (:Year {opCo18Year: tointeger(substring(input.Capture_Datetime_vod__c, 0, 4))+2})-[:HAS_MONTH]->(:Month {opCo18Month: tointeger(substring(input.Capture_Datetime_vod__c, 5, 2))})-[:HAS_DAY]->(d:Day {opCo18Day: tointeger(substring(input.Capture_Datetime_vod__c, 8, 2))})<-[:NEXT_DAY]-(dt:Day)
MERGE (c:Consent{consentId:input.IRDA_SYS_OBJECT_GUID, input.IRDA_SYS_COUNTRY,input.Channel_Label_vod__c, input.Name,   input.Opt_Expiration_Date_vod__c,input.Opt_Type_vod__c, opCo18ObjCreatedBy:VarCreatedBy})
ON CREATE SET c.opCo18ObjCreatedAt=VarCreatedDate, c.opCo18Uuid=apoc.create.uuid(), c.accountId = input.Account_vod__c
MERGE (c)-[rd:HAS_RAW_DATA]->(n)
ON CREATE SET rd.opCo18ObjCreatedBy=VarCreatedBy, rd.opCo18ObjCreatedAt=VarCreatedDate, rd.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[vf:IS_VALID_FOR]->(ct)
ON CREATE SET vf.opCo18ObjCreatedBy=VarCreatedBy, vf.opCo18ObjCreatedAt=VarCreatedDate, vf.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[vfc:IS_VALID_FOR]->(cxt)
ON CREATE SET vfc.opCo18ObjCreatedBy=VarCreatedBy, vfc.opCo18ObjCreatedAt=VarCreatedDate, vfc.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[vfd:IS_VALID_FROM_DATE]->(df)
ON CREATE SET vfd.opCo18ObjCreatedBy=VarCreatedBy, vfd.opCo18ObjCreatedAt=VarCreatedDate, vfd.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[vtd:IS_VALID_TO_DATE]->(dt)
ON CREATE SET vtd.opCo18ObjCreatedBy=VarCreatedBy, vtd.opCo18ObjCreatedAt=VarCreatedDate, vtd.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[ac:AGREES_MAILING]->(psd:PersonalData {mailAddress: input.Channel_Value_vod__c, opCo18ObjCreatedBy:VarCreatedBy, opCo18ObjCreatedAt:VarCreatedDate,opCo18Uuid:apoc.create.uuid()})
ON CREATE SET ac.opCo18ObjCreatedBy=VarCreatedBy, ac.opCo18ObjCreatedAt=VarCreatedDate, ac.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[as:AGREES_STORING]->(psd)
ON CREATE SET as.opCo18ObjCreatedBy=VarCreatedBy, as.opCo18ObjCreatedAt=VarCreatedDate, as.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[ivf:IS_VALID_FOR]->(cntx:Context {personalMedicalInterest:'', opCo18ObjCreatedBy:VarCreatedBy, opCo18ObjCreatedAt:VarCreatedDate, opCo18Uuid:apoc.create.uuid()})
ON CREATE SET ivf.opCo18ObjCreatedBy=VarCreatedBy, ivf.opCo18ObjCreatedAt=VarCreatedDate, ivf.opCo18Uuid=apoc.create.uuid()
'
WHERE  RULE_ID = 1 ;
commit;


update  SOURCE_SYSTEM_A_OP.ETL_HARMONIZED_COMPILATION_RULE
set compilation_rule = '
MATCH (n:RawNGSFNordicsAEmail)
WITH n AS input, ''#OCB#'' AS VarCreatedBy, ''#OCD#'' AS VarCreatedDate
MATCH (n:RawNGSFNordicsAEmail {IRDA_SYS_OBJECT_GUID:input.IRDA_SYS_OBJECT_GUID})
MATCH (ct:Context {businessArea: ''Pharma''})
MATCH (cxt:Context {country:LEFT(input.BPH_External_ID__c,2)})
MATCH (:Year {opCo18Year: tointeger(substring(input.Capture_Datetime_vod__c, 0, 4))})-[:HAS_MONTH]->(:Month {opCo18Month: tointeger(substring(input.Capture_Datetime_vod__c, 5, 2))})-[:HAS_DAY]->(df:Day {opCo18Day: tointeger(substring(input.Capture_Datetime_vod__c, 8, 2))})
MATCH (:Year {opCo18Year: tointeger(substring(input.Capture_Datetime_vod__c, 0, 4))+2})-[:HAS_MONTH]->(:Month {opCo18Month: tointeger(substring(input.Capture_Datetime_vod__c, 5, 2))})-[:HAS_DAY]->(d:Day {opCo18Day: tointeger(substring(input.Capture_Datetime_vod__c, 8, 2))})<-[:NEXT_DAY]-(dt:Day)
MERGE (c:Consent{consentId:input.IRDA_SYS_OBJECT_GUID, opCo18ObjCreatedBy:VarCreatedBy})
ON CREATE SET c.opCo18ObjCreatedAt=VarCreatedDate, c.opCo18Uuid=apoc.create.uuid(), c.accountId = input.Account_vod__c
MERGE (c)-[rd:HAS_RAW_DATA]->(n)
ON CREATE SET rd.opCo18ObjCreatedBy=VarCreatedBy, rd.opCo18ObjCreatedAt=VarCreatedDate, rd.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[vf:IS_VALID_FOR]->(ct)
ON CREATE SET vf.opCo18ObjCreatedBy=VarCreatedBy, vf.opCo18ObjCreatedAt=VarCreatedDate, vf.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[vfc:IS_VALID_FOR]->(cxt)
ON CREATE SET vfc.opCo18ObjCreatedBy=VarCreatedBy, vfc.opCo18ObjCreatedAt=VarCreatedDate, vfc.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[vfd:IS_VALID_FROM_DATE]->(df)
ON CREATE SET vfd.opCo18ObjCreatedBy=VarCreatedBy, vfd.opCo18ObjCreatedAt=VarCreatedDate, vfd.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[vtd:IS_VALID_TO_DATE]->(dt)
ON CREATE SET vtd.opCo18ObjCreatedBy=VarCreatedBy, vtd.opCo18ObjCreatedAt=VarCreatedDate, vtd.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[ac:AGREES_MAILING]->(psd:PersonalData {mailAddress: input.Channel_Value_vod__c, opCo18ObjCreatedBy:VarCreatedBy, opCo18ObjCreatedAt:VarCreatedDate,opCo18Uuid:apoc.create.uuid()})
ON CREATE SET ac.opCo18ObjCreatedBy=VarCreatedBy, ac.opCo18ObjCreatedAt=VarCreatedDate, ac.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[as:AGREES_STORING]->(psd)
ON CREATE SET as.opCo18ObjCreatedBy=VarCreatedBy, as.opCo18ObjCreatedAt=VarCreatedDate, as.opCo18Uuid=apoc.create.uuid()
MERGE (c)-[ivf:IS_VALID_FOR]->(cntx:Context {personalMedicalInterest:'', opCo18ObjCreatedBy:VarCreatedBy, opCo18ObjCreatedAt:VarCreatedDate, opCo18Uuid:apoc.create.uuid()})
ON CREATE SET ivf.opCo18ObjCreatedBy=VarCreatedBy, ivf.opCo18ObjCreatedAt=VarCreatedDate, ivf.opCo18Uuid=apoc.create.uuid()
'
WHERE  RULE_ID = 1 ;
commit;
