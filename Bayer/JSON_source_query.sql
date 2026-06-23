
SELECT    crm_system.Multichannel_Consent_vod__c."Id",
          replace(crm_system.Multichannel_Consent_vod__c.Disclaimer_Text_vod__c,'"',''''),
		  'WITH apoc.convert.fromJsonMap(''{'
           +'"irdaSysCountry":'+ '"' +  ISNULL(CONVERT(varchar(100), crm_system.Multichannel_Consent_vod__c.IRDA_SYS_COUNTRY),'NULL') + '",'
		   +'"DELETED":'+ '"' +  ISNULL(CONVERT(varchar(100),crm_system.Multichannel_Consent_vod__c.IRDA_SYS_DELETED),'NULL') + '",'
           +'"IS_DELETED":'+ '"' +  ISNULL(CONVERT(varchar(100),crm_system.Multichannel_Consent_vod__c.IRDA_SYS_IS_DELETED),'NULL') + '",'
		   +'"ID":'+ '"' + ISNULL(CONVERT(varchar(100),crm_system.Multichannel_Consent_vod__c."Id"),'NULL') + '",'
           +'"accountId":'+ '"' +  ISNULL(CONVERT(varchar(100),crm_system.Multichannel_Consent_vod__c.Account_vod__c),'NULL') + '",'
		   +'"captureDateTime":'+ '"' +  ISNULL(CONVERT(varchar(100),crm_system.Multichannel_Consent_vod__c.Capture_Datetime_vod__c),'NULL') + '",'
           +'"consentText":'+ '"' + ISNULL(CONVERT(varchar(4000),crm_system.Multichannel_Consent_vod__c.Default_Consent_Text_vod__c),'NULL') + '",'
           +'"disclamerText":'+ '"' + ISNULL(CONVERT(varchar(4000),replace(crm_system.Multichannel_Consent_vod__c.Disclaimer_Text_vod__c,'"','\''')),'NULL') + '",'
		   +'"optExpirationDate":'+ '"' + ISNULL(CONVERT(varchar(100),crm_system.Multichannel_Consent_vod__c.Opt_Expiration_Date_vod__c),'NULL') + '",'
           +'"Name":'+ '"' + ISNULL(CONVERT(varchar(100),crm_system.Multichannel_Consent_vod__c.Name),'NULL') + '",'
           +'"optType":'+ '"' + ISNULL(CONVERT(varchar(100),crm_system.Multichannel_Consent_vod__c.Opt_Type_vod__c),'NULL') + '",'
           +'"channelLabel":'+ '"' + ISNULL(CONVERT(varchar(100),crm_system.Consent_Type_vod__c.Channel_Label_vod__c),'NULL') + '",'
           +'"productName":'+ '"' + ISNULL(CONVERT(varchar(100),crm_system.Product_vod__c.Name),'NULL') + '"'
		   +'}'') as data unwind data'  as JSON_FORMAT
FROM  crm_system.Multichannel_Consent_vod__c
LEFT JOIN crm_system.Consent_Type_vod__c on crm_system.Multichannel_Consent_vod__c.Consent_Type_vod__c =
 crm_system.Consent_Type_vod__c.Id
LEFT JOIN crm_system.Product_vod__c on crm_system.Multichannel_Consent_vod__c.Product_vod__c =
 crm_system.Product_vod__c.Id


WITH apoc.convert.fromJsonMap('{"irdaSysCountry":"SE","DELETED":"NULL","IS_DELETED":"NULL","ID":"PLACEHOLDER_ID","accountId":"PLACEHOLDER_ID","captureDateTime":"PLACEHOLDER_DATE","consentText":"PLACEHOLDER_CONSENT_TEXT","disclamerText":"PLACEHOLDER_DISCLAIMER_TEXT","optExpirationDate":"2047-12-01","Name":"MCC-PLACEHOLDER","optType":"Opt_In_vod","channelLabel":"CLM","productName":"NULL"}') as data unwind data
as q
MERGE (raw:RawMccConsent
{DisclamerText: q.disclamerText,
ConsentText: q.consentText,
ChannelLabel: q.channelLabel,
AccountId: q.accountId,
CaptureDateTime: q.captureDateTime,
OptExpirationDate: q.optExpirationDate,
Name: q.Name,
OptType: q.optType,
ProductName: q.productName,
IRDASysCountry: q.irdaSysCountry})



WITH apoc.convert.fromJsonMap('{"irdaSysCountry":"SE","DELETED":"NULL","IS_DELETED":"NULL","ID":"PLACEHOLDER_ID","accountId":"PLACEHOLDER_ID","captureDateTime":"PLACEHOLDER_DATE","consentText":"PLACEHOLDER_CONSENT_TEXT","disclamerText":"PLACEHOLDER_DISCLAIMER_TEXT","optExpirationDate":"2047-12-01","Name":"MCC-PLACEHOLDER","optType":"Opt_In_vod","channelLabel":"CLM","productName":"NULL"}') as data unwind data
as q
MERGE (raw:RawMccConsent
{DisclamerText: q.disclamerText,
ConsentText: q.consentText,
ChannelLabel: q.channelLabel,
AccountId: q.accountId,
CaptureDateTime: q.captureDateTime,
OptExpirationDate: q.optExpirationDate,
Name: q.Name,
OptType: q.optType,
ProductName: q.productName,
IRDASysCountry: q.irdaSysCountry})
