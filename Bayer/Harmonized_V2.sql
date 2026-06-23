
LOAD CSV WITH HEADERS FROM "file:///talend_in/products.csv" AS row
CREATE (n:Product)
SET n = row



WITH {} as props
WITH 'file:///talend_in/xml_converted.json' AS url
CALL apoc.load.json(url) YIELD value
UNWIND value.row AS props
CREATE (ref:RawMccConsent) SET ref = props



WITH {} as props
WITH 'file:///talend_in/xml_converted.json' AS url
CALL apoc.load.json(url) YIELD value
UNWIND value.row AS props
CREATE (ref:RawMccConsent) SET ref = props


match objectcreated_id = ?
delete

MATCH (n:RawMccConsent)
WHERE n.ChannelLabel IS NOT NULL AND n.ConsentText IS NOT NULL
AND n.OptExpirationDate IS NOT NULL AND n.AccountId IS NOT NULL
AND n.CaptureDateTime IS NOT NULL AND n.OptType IS NOT NULL
AND n.IRDASysCountry IS NOT NULL AND n.Name IS NOT NULL
WITH n AS input
MERGE (c:Consent:CLM {SSLK:input.AccountId, ChannelLabel: input.ChannelLabel})
MERGE (so:SubordinateLkp {SSLK:input.AccountId})
MERGE (d:Date {date:input.CaptureDateTime})
MERGE (e:OptExpirationDate{expdate:input.OptExpirationDate})
MERGE (g:IRDASysCountry{country:input.IRDASysCountry})
MERGE (h:ChannelLabel {Label:input.ChannelLabel})
MERGE (n:RawMccConsent{AccountId:input.AccountId})
MERGE (c)-[:IS_VALID_FROM]->(d)
MERGE (c)-[:IS_VALID_UNTIL]->(e)
MERGE (c)-[:IS_VALID_FOR]->(g)


MATCH ()-[r]-() WHERE r.objCreatedBy = '1' DETACH DELETE r
MATCH (n {objCreatedBy:'1'}) DETACH DELETE n

call dbms.showCurrentUser() yield username as un, roles, flags
with apoc.date.format(apoc.date.currentTimestamp(),'ms', 'yyyy-MM-dd HH:mm:ss', 'UTC') as ct, un
objectcreated_id = ?

match (c:Consent)-[:HAS_RAWDATA]->(rc:RawMccConsent)

match (:Year {year: tointeger(substring(rc.Capture_Datetime_vod__c, 0, 4))})-[:HAS_MONTH]->(:Month {month: tointeger(substring
(rc.Capture_Datetime_vod__c, 5, 2))})-[:HAS_DAY]->(df:Day {day: tointeger(substring(rc.Capture_Datetime_vod__c, 8, 2))})

match (:Year {year: tointeger(substring(rc.GivenDate, 0, 4))+1})-[:HAS_MONTH]->(:Month {month: tointeger(substring
(rc.GivenDate, 5, 2))})-[:HAS_DAY]->(:Day{day: tointeger(substring(rc.GivenDate, 8, 2))})<-[:NEXT]-(dt:Day)

match (ct:Context {businessArea: 'Pharma'})

create (c)-[:IS_VALID_FROM_DATE {objCreatedBy:un, objCreatedAt:ct}]->(df)
create (c)-[:IS_VALID_TO_DATE {objCreatedBy:un, objCreatedAt:ct}]->(dt)

create (c)-[:IS_VALID_FOR {objCreatedBy:un, objCreatedAt:ct}]->(ct)

create (c)-[:AGREES_MAILING  {objCreatedBy:un, objCreatedAt:ct}]->
  (pd:PersonalData  {objCreatedBy:un, objCreatedAt:ct})
create (c)-[:AGREES_CALLING  {objCreatedBy:un, objCreatedAt:ct}]->(pd)

create (c)-[:AGREES_STORING  {objCreatedBy:un, objCreatedAt:ct}]->
  (um:UseOfElectronicMedia  {objCreatedBy:un, objCreatedAt:ct})
create (c)-[:AGREES_ANAYZING  {objCreatedBy:un, objCreatedAt:ct}]->(um)




call dbms.showCurrentUser() yield username as un, roles, flags
with apoc.date.format(apoc.date.currentTimestamp(),'ms', 'yyyy-MM-dd HH:mm:ss', 'UTC') as ct, un

match (c:Consent)-[:HAS_RAWDATA]->(rc:RawDemoMail1Consent)

match (:Year {year: tointeger(substring(rc.GivenDate, 0, 4))})-[:HAS_MONTH]->(:Month {month: tointeger(substring
(rc.GivenDate, 5, 2))})-[:HAS_DAY]->(df:Day {day: tointeger(substring(rc.GivenDate, 8, 2))})

match (:Year {year: tointeger(substring(rc.GivenDate, 0, 4))+1})-[:HAS_MONTH]->(:Month {month: tointeger(substring
(rc.GivenDate, 5, 2))})-[:HAS_DAY]->(:Day{day: tointeger(substring(rc.GivenDate, 8, 2))})<-[:NEXT]-(dt:Day)

match (ct:Context {webDomain: rc.Domain})

create (c)-[:IS_VALID_FROM_DATE {objCreatedBy:un, objCreatedAt:ct}]->(df)
create (c)-[:IS_VALID_TO_DATE {objCreatedBy:un, objCreatedAt:ct}]->(dt)

create (c)-[:IS_VALID_FOR {objCreatedBy:un, objCreatedAt:ct}]->(ct)

create (c)-[:AGREES_COMMUNICATE  {objCreatedBy:un, objCreatedAt:ct}]->
  (pd:PersonalData  {mailAddress: rcMailAddress, objCreatedBy:un, objCreatedAt:ct})
create (c)-[:AGREES_STORAGE  {objCreatedBy:un, objCreatedAt:ct}]->(pd)

match (c:Consent)-[:HAS_RAWDATA]->(rc:RawDemoMail1Consent) where id(c)=6296
match (:Year {year: tointeger(substring(rc.GivenDate, 0, 4))})-[:HAS_MONTH]->(:Month {month: tointeger(substring(rc.GivenDate, 5, 2))})-[:HAS_DAY]->(df:Day {day: tointeger(substring(rc.GivenDate, 8, 2))})
match (:Year {year: tointeger(substring(rc.GivenDate, 0, 4))+1})-[:HAS_MONTH]->(:Month {month: tointeger(substring(rc.GivenDate, 5, 2))})-[:HAS_DAY]->(:Day {day: tointeger(substring(rc.GivenDate, 8, 2))})<-[:NEXT]-(dt:Day)
match (ct:Context {webDomain: rc.Domain})
create (c)-[:IS_VALID_FROM_DATE {objCreatedBy:'hana_user', objCreatedAt:'PLACEHOLDER_DATE'}]->(df)
create (c)-[:IS_VALID_TO_DATE {objCreatedBy:'hana_user', objCreatedAt:'PLACEHOLDER_DATE'}]->(dt)
create (c)-[:IS_VALID_FOR {objCreatedBy:'hana_user', objCreatedAt:'PLACEHOLDER_DATE'}]->(ct)
create (c)-[:AGREES_COMMUNICATE {objCreatedBy:'hana_user', objCreatedAt:'PLACEHOLDER_DATE'}]->(pd:PersonalData  {mailAddress: rc.MailAddress, objCreatedBy:'hana_user', objCreatedAt:'PLACEHOLDER_DATE'})
create (c)-[:AGREES_STORAGE {objCreatedBy:'hana_user', objCreatedAt:'PLACEHOLDER_DATE'}]->(pd)
return *
