SELECT
            crm_system.Multichannel_Consent_vod__c.IRDA_SYS_COUNTRY,
            crm_system.Multichannel_Consent_vod__c.IRDA_SYS_DELETED,
            crm_system.Multichannel_Consent_vod__c.IRDA_SYS_IS_DELETED,
            crm_system.Multichannel_Consent_vod__c."Id",
            crm_system.Multichannel_Consent_vod__c.Account_vod__c,
            crm_system.Multichannel_Consent_vod__c.Capture_Datetime_vod__c,
            crm_system.Multichannel_Consent_vod__c.Default_Consent_Text_vod__c,
            crm_system.Multichannel_Consent_vod__c.Disclaimer_Text_vod__c,
            crm_system.Multichannel_Consent_vod__c.Opt_Expiration_Date_vod__c,
            crm_system.Multichannel_Consent_vod__c.Name,
            crm_system.Multichannel_Consent_vod__c.Opt_Type_vod__c,
            crm_system.Consent_Type_vod__c.Channel_Label_vod__c,
            crm_system.Product_vod__c.Name,
            1 as constantOne
FROM  crm_system.Multichannel_Consent_vod__c
LEFT JOIN crm_system.Consent_Type_vod__c on crm_system.Multichannel_Consent_vod__c.Consent_Type_vod__c =
 crm_system.Consent_Type_vod__c.Id
LEFT JOIN crm_system.Product_vod__c on crm_system.Multichannel_Consent_vod__c.Product_vod__c =
 crm_system.Product_vod__c.Id
