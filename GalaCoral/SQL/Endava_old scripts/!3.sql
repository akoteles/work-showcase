



Create TABLE AR_TEST AS


        SELECT
          arit.ar_item_type
          ,arit.ar_item_id AR_ITEM_ID
          ,arit.item_ref ITEM_REF
          ,arit.creation_date ACCOUNTING_DATETIME
          ,arar.appl_jrnl_code APPL_JRNL_CODE
          ,1 JOURNAL_CODE
          ,2 JOURNAL_DATETIME
          ,3 JOURNAL_LINE
          ,arar.account_code ACCOUNT_CODE
          ,arar.dept DEPT
          ,4 PROJECT_CODE
          ,arar.affiliate AFFILIATE
          ,arit.currency_code ACCOUNT_ENTRY_CURR
          ,arit.currency_code FOREIGN_CURR
          ,1 EXCHANGE_RATE
          ,arit.creation_date EXCHANGE_RATE_DATETIME
          ,arar.line_description LINE_DESC
          ,'N' PROCESSED_IND
          ,7 PROCESSED_DATETIME
          ,'Default' CNTL_PROCESS
          ,'SYSTEM' CNTL_USER_ID
          ,sysdate CNTL_TIMESTAMP
          ,1 CNTL_LOCKSEQ
          ,'N' MONETARY_AMOUNT_SUM_ZERO_IND
          ,5 PAYMENT_SEQ
          ,1 BATCH_ID
          ,arar.rule_id
          ,arar.dr_cr
          ,AR_REC.tax_recharge_indicator
          ,AR_REC.is_tax
          ,arar.BUSINESS_UNIT_RULE
          ,arar.GL_BUSINESS_UNIT_RULE
          ,arar.PRODUCT_RULE
          ,arar.ACCOUNT_CURRENCY_RULE
          ,arar.MONETARY_AMOUNT_RULE
          ,arar.FOREIGN_AMOUNT_RULE
          ,AR_REC.PRODUCT_CODE
          ,arar.PROJECT_CODE_RULE
      ,AR_REC.country_code
      ,AR_REC.item_element_ref
      ,AR_REC.item_element_type
        FROM AR_REC
        JOIN ar_items arit on arit.ar_item_id = AR_REC.ar_item_id
        JOIN ar_accounting_rules arar on arit.ar_item_type = arar.item_type
          AND AR_REC.is_tax  = arar.is_tax
        WHERE arit.ar_item_id = 4770
      AND arar.active = 'Y'




      Create TABLE AR_REC as


        SELECT t.*, rownum rn FROM (
        SELECT DISTINCT aipe.ar_item_id,aipe.product_code, 'N' is_tax,aipe.insurer_id,'*' country_code, aipe.tax_recharge_indicator, aipe.item_element_ref, 'P' item_element_type
        FROM ar_item_insurer_prod_elements aipe
        WHERE aipe.ar_item_id = 4770
        UNION ALL
        SELECT DISTINCT aite.ar_item_id, aite.product_code, 'Y' is_tax,aite.insurer_id,aite.country_code, null tax_recharge_indicator, aite.item_element_ref, 'T' item_element_type
        FROM ar_item_insurer_country_taxes aite
        WHERE aite.ar_item_id = 4770
      )t
