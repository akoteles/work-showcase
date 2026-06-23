SELECT P3.ID C1_ID,
       P3.list45_id C2_FLUSH_PROCEDURE_LIST_SEL,
       P3.list46_id C3_FLUSH_PROCEDURE_AUTO_SEL,
       P3.list36_id C4_DATE_PRICE_BELLMARK_LIST_SE,
       P3.list37_id C5_DATE_PRICE_BELLMARK_AUTO_SE,
       P3.list50_id C6_CASE_PALLET_LABEL_AUTO_SEL,
       P3.list38_id C7_PALLET_CONFIG_AUTO_TEMPLATE,
       P3.list32_id C8_PROMO_MATERIAL_LIST_SEL,
       P3.list47_id C9_TRANSPORTATION_LIST_SEL,
       P3.list48_id C10_TRANSPORTATION_AUTO_SEL,
       P3.list42_id C11_TRANSFER_PRICING_LIST_SEL,
       1 C12_CUSTOMS_REVIEW_REQ,
       P3.list51_id C13_COST_ACCNT_AUTO_SEL,
       P3.list31_id C14_OBSOLESCENCE_RISK,
       P3.text39 C15_IF_YES,
       P3.list33_id C16_OBSOLESCENCE_OWNER,
       P3.list35_id C17_BUDGET_YEAR_IMPACTED,
       P3.text40 C18_IF_NO,
       P3.list39_id C19_REASON_STATEMENT,
       P3.list40_id C20_OBSOLESCENCE_AUTO_SEL,
       P3.list34_id C21_CONTACT_RESOURCE_LIST_SEL,
       P3.list54_id C22_CONTACT_RESOURCE_AUTO_TEMP,
       P3.list52_id C23_BP_FORM_LOCKED,
       P3.multilist31 C24_HIDDEN_USERS_FIELD,
       P3.CREATE_DATE C25_ETL_CREATE_DATE,
       P3.UPDATE_DATE C26_ETL_UPDATE_DATE
  FROM planning_schema.planning_schema_PAGE_THREE P3
 WHERE     (1 = 1)
       AND (   to_date(P3.CREATE_DATE, 'DD/MM/YYYY HH24:MI:SS')
               >= TO_DATE ('&PLAN_MODULE.V_DATE_TO', 'DD/MM/YYYY HH24:MI:SS')
            OR to_date(P3.UPDATE_DATE, 'DD/MM/YYYY HH24:MI:SS') >=
                  to_date('&PLAN_MODULE.V_DATE_TO', 'DD/MM/YYYY HH24:MI:SS') )
       AND (P3.CLASS_ID = 9000)


       select to_date(TO_char ('01/01/1900 00:00:00'), 'DD/MM/YYYY HH24:MI:SS') from dual

       select * from planning_schema_PAGE_THREE where to_date(to_char(create_date,'DDMMYYYY')) > to_date(TO_char (&V_DATE_TO, 'DDMMYYYY'))
