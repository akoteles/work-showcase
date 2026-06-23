cypher-shell -u graph_user -p PLACEHOLDER_SECRET

MATCH (n:RefRawMailConsent) DELETE n;

LOAD CSV WITH HEADERS FROM "file:///IRDA_sample.csv" AS row
CREATE (n:RefRawMailConsent)
SET n = row;

match (rrc:RefRawMailConsent)
create (rrc)
  -[r1:REF_REPRESENTED_BY{objCreatedBy:graph_user, objCreatedAt:ct}]->
 (rc:RefConsent {objCreatedBy:graph_user, objCreatedAt:ct});

call dbms.showCurrentUser() yield username as un, roles, flags
call apoc.date.format(apoc.date.currentTimestamp(),'ms', 'yyyy-MM-dd HH:mm:ss', 'CET') as ct, un



with 'C:/_data/' as url
CALL apoc.load.json(url) YIELD value as person
RETURN *




LOAD CSV WITH HEADERS FROM "file:///IRDA_sample_100k.csv" AS row
CREATE (n:RefRawMailConsent_100k)
SET n = row;


call dbms.showCurrentUser() yield username as un
with apoc.date.format(apoc.date.currentTimestamp(),'ms', 'yyyy-MM-dd HH:mm:ss', 'CET') as ct, un

match (rrc:RefRawMailConsent)
create (rrc)
  -[r1:REF_REPRESENTED_BY{objCreatedBy:un, objCreatedAt:ct}]->
 (rc:RefConsent {objCreatedBy:un, objCreatedAt:ct})


call dbms.showCurrentUser() yield username as un
with apoc.date.format(apoc.date.currentTimestamp(),'ms', 'yyyy-MM-dd HH:mm:ss', 'CET') as ct, un

create (rc)
  -[r2:REF_IS_VALID_FOR {objCreatedBy:un, objCreatedAt:ct}]->
  (rvalid:RefValidity
   {startDate:"rc.GivenDate"
    ,endDate:"rc.GivenDate + 1 year"
    ,objCreatedBy:un, objCreatedAt:ct})

create (rc)
  -[r3:REF_IS_VALID_FOR {objCreatedBy:un, objCreatedAt:ct}]->
  (rcont:RefContext
   {webDomain:"rc.Domain"
    ,objCreatedBy:un, objCreatedAt:ct})

create (rc)
  -[r4:REF_AGREES {objCreatedBy:un, objCreatedAt:ct}]->
  (rstore:RefStore {objCreatedBy:un, objCreatedAt:ct})

create (rstore)
  -[r5:REF_USE_ON {objCreatedBy:un, objCreatedAt:ct}]->
  (rpd:RefPersonalData
   {mailAddress: "rc.MailAddress"
    ,objCreatedBy:un, objCreatedAt:ct})

create (rc)
  -[r6:REF_AGREES {objCreatedBy:un, objCreatedAt:ct}]->
  (rcomm:RefCommunicate {objCreatedBy:un, objCreatedAt:ct})

create (rcomm)
  -[r7:REF_USE_ON {objCreatedBy:un, objCreatedAt:ct}]->
 (rpd)
return *



LOAD CSV WITH HEADERS FROM "file:///IRDA_sample.csv" AS row
CREATE (n:RefRawMailConsent)
SET n = row,
  n.SourceSystem = toFloat(row.unitPrice),
  n.unitsInStock = toInteger(row.unitsInStock), n.unitsOnOrder = toInteger(row.unitsOnOrder),
  n.reorderLevel = toInteger(row.reorderLevel), n.discontinued = (row.discontinued <> "0")


SourceSystem,PersonalID,ConsentID,MailAddress,GivenDate,
SOURCE_SYSTEM_A,PLACEHOLDER_ID,PLACEHOLDER_ID,user@example.com,03.10.2017,DRUG_A.example.com,
