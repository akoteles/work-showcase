CREATE OR REPLACE PROCEDURE `client-social-data-lake.consumer.prc_fact_monthly_entity_stats`()
BEGIN

    MERGE `client-social-data-lake.consumer.fact_monthly_entity_stats` AS t
    USING ( select t1.*,
                   current_timestamp() as etl_update_ts,
                   current_timestamp() as etl_insert_ts
             from (
                select  t.Exchange_Name,
                        FORMAT_DATE('%Y-%m', DATE_TRUNC(t.api_date, MONTH)) Year_Month,
                        case when lower(trim(Exchange_Name)) ='exchange_a' then
                             case when lower(trim(invitecode)) like '%entity_01%' then 'ENTITY_01'
                                  when lower(trim(invitecode)) like '%entity_02%' then 'ENTITY_02'
                                  when lower(trim(invitecode)) like '%entity_03%' then 'ENTITY_03'
                                  when lower(trim(invitecode)) like '%entity_04%' then 'ENTITY_03'
                                  when lower(trim(invitecode)) like '%entity_05%' then 'ENTITY_05'
                                  when lower(trim(invitecode)) like '%entity_06%' then 'ENTITY_06'
                                  when lower(trim(invitecode)) like '%entity_07%' then 'ENTITY_07'
                                  when lower(trim(invitecode)) like '%entity_08%' then 'ENTITY_08'
                                  when lower(trim(invitecode)) like '%entity_09%' then 'ENTITY_09'
                                  when lower(trim(invitecode)) like '%entity_10%' then 'ENTITY_10'
                                  when lower(trim(invitecode)) like '%entity_11%' then 'ENTITY_11'
                                  when lower(trim(invitecode)) like '%entity_12%' then 'ENTITY_12'
                                  when lower(trim(invitecode)) like '%entity_13%' then 'ENTITY_13'
                                  when lower(trim(invitecode)) like '%entity_14%' then 'ENTITY_14'
                                  when lower(trim(invitecode)) like '%entity_15%' then 'ENTITY_15'
                                  when lower(trim(invitecode)) like '%entity_16%' then 'ENTITY_16'
                                  when lower(trim (account_id)) = 'main_affiliate_account' and lower(trim(invitecode)) = 'default' then 'ENTITY_02'
                                  when lower(trim (account_id)) = 'school_affiliate@example-platform.com' and lower(trim(invitecode)) = 'default' then 'ENTITY_06'
                                  when lower(trim (account_id)) = 'entity_03_main' then 'ENTITY_03'
                                  when lower(trim (account_id)) = 'entity_13_main' then 'ENTITY_13'
                                  when lower(trim (account_id)) = 'entity_12_main' then 'ENTITY_12'
                                  else 'OTHER'
                                end
                            when lower(trim(Exchange_Name)) ='exchange_b' then
                              case when lower(trim(invitecode)) like '%entity_01%' then 'ENTITY_01'
                                  when lower(trim(invitecode)) like '%entity_02%' then 'ENTITY_02'
                                  when lower(trim(invitecode)) like '%main_aff%' then 'ENTITY_02'
                                  when lower(trim(invitecode)) like '%promo_code_1%' then 'ENTITY_02'
                                  when lower(trim(invitecode)) like '%promo_code_2%' then 'ENTITY_02'
                                  when lower(trim(invitecode)) like '%entity_03%' then 'ENTITY_03'
                                  when lower(trim(invitecode)) like '%entity_04%' then 'ENTITY_03'
                                  when lower(trim(invitecode)) like '%entity_05%' then 'ENTITY_05'
                                  when lower(trim(invitecode)) like '%promo_code_3%' then 'ENTITY_05'
                                  when lower(trim(invitecode)) like '%entity_06%' then 'ENTITY_06'
                                  when lower(trim(invitecode)) like '%entity_07%' then 'ENTITY_07'
                                  when lower(trim(invitecode)) like '%entity_08%' then 'ENTITY_08'
                                  when lower(trim(invitecode)) like '%entity_09%' then 'ENTITY_09'
                                  when lower(trim(invitecode)) like '%entity_10%' then 'ENTITY_10'
                                  when lower(trim(invitecode)) like '%entity_11%' then 'ENTITY_11'
                                  when lower(trim(invitecode)) like '%promo_code_4%' then 'ENTITY_11'
                                  when lower(trim(invitecode)) like '%promo_code_5%' then 'ENTITY_11'
                                  when lower(trim(invitecode)) like '%entity_13%' then 'ENTITY_13'
                                  when lower(trim(invitecode)) like '%entity_14%' then 'ENTITY_14'
                                  when lower(trim(invitecode)) like '%entity_15%' then 'ENTITY_15'
                                  when lower(trim(invitecode)) like '%entity_16%' then 'ENTITY_16'
                                  when lower(trim(invitecode)) like '%entity_17%' then 'ENTITY_17'
                                  when lower(trim(invitecode)) like '%entity_18%' then 'ENTITY_18'
                                  else 'OTHER'
                                end
                            when lower(trim(Exchange_Name)) ='exchange_c' then
                              case when lower(trim (account_id)) = 'entity_03_school'                  then 'ENTITY_03'
                                  when lower(trim (account_id)) = 'entity_05_tier_1'                   then 'ENTITY_05'
                                  when lower(trim (account_id)) = 'entity_09_promo_1'                  then 'ENTITY_09'
                                  when lower(trim (account_id)) = 'entity_09_signup'                   then 'ENTITY_09'
                                  when lower(trim (account_id)) = 'social_channel'                     then 'ENTITY_10'
                                  when lower(trim (account_id)) = 'entity_05_tier_2'                   then 'ENTITY_05'
                                  when lower(trim (account_id)) = 'entity_13_main'                     then 'ENTITY_13'
                                  when lower(trim (account_id)) = 'entity_08_main'                     then 'ENTITY_08'
                                  when lower(trim (account_id)) = 'main_affiliate'                     then 'ENTITY_02'
                                  when lower(trim (account_id)) = 'entity_01_main'                     then 'ENTITY_01'
                                  else 'OTHER'
                              end
                            when lower(trim(Exchange_Name)) ='exchange_d' then
                              CASE WHEN lower(trim (account_id)) = 'affiliate@example-platform.com'                   THEN 'ENTITY_02'
                                  WHEN lower(trim (account_id)) = 'entity_05@example-platform.com'                   THEN 'ENTITY_05'
                                  WHEN lower(trim (account_id)) = 'entity_03@example-platform.com'                   THEN 'ENTITY_03'
                                  WHEN lower(trim (account_id)) = 'entity_16@example-platform.com'                   THEN 'ENTITY_16'
                                  WHEN lower(trim (account_id)) = 'entity_11@example-platform.com'                   THEN 'ENTITY_11'
                                  WHEN lower(trim (account_id)) = 'entity_14@example-platform.com'                   THEN 'ENTITY_14'
                                  WHEN lower(trim (account_id)) = 'entity_08@example-platform.com'                   THEN 'ENTITY_08'
                                  WHEN lower(trim (account_id)) = 'entity_01@example-platform.com'                   THEN 'ENTITY_01'
                                  WHEN lower(trim (account_id)) = 'entity_13@example-platform.com'                   THEN 'ENTITY_13'
                                  WHEN lower(trim (account_id)) = 'entity_15@example-platform.com'                   THEN 'ENTITY_15'
                                  WHEN lower(trim (account_id)) = 'entity_07@example-platform.com'                   THEN 'ENTITY_07'
                                  WHEN lower(trim (account_id)) = 'entity_12@example-platform.com'                   THEN 'ENTITY_12'
                                  WHEN lower(trim (account_id)) = 'entity_06@example-platform.com'                   THEN 'ENTITY_06'
                                  WHEN lower(trim (account_id)) = 'easyalgo.affiliate@example-platform.com'          THEN 'EASYALGO'
                                  WHEN lower(trim (account_id)) = 'entity_05_club@example-platform.com'              THEN 'ENTITY_05'
                                  WHEN lower(trim (account_id)) = 'affiliate+social@example-platform.com'            THEN 'ENTITY_02'
                                  WHEN lower(trim (account_id)) = 'hustle.affiliate@example-platform.com'            THEN 'ENTITY_15'
                                  WHEN lower(trim (account_id)) = 'entity_13_accelerate@example-platform.com'        THEN 'ENTITY_13'
                                  WHEN lower(trim (account_id)) = 'entity_09@example-platform.com'                   THEN 'ENTITY_09'
                                  WHEN lower(trim (account_id)) = 'intro2school@example-platform.com'                THEN 'ENTITY_06'
                                  WHEN lower(trim (account_id)) = 'intro2school+account2@example-platform.com'       THEN 'ENTITY_06'
                                  WHEN lower(trim (account_id)) = 'entity_12+2ndaccount@example-platform.com'        THEN 'ENTITY_12'
                                  WHEN lower(trim (account_id)) = 'entity_05_main+2ndaccount@example-platform.com'   THEN 'ENTITY_05'
                                  WHEN lower(trim (account_id)) = 'entity_03_main+2ndaccount@example-platform.com'   THEN 'ENTITY_03'
                                  WHEN lower(trim (account_id)) = 'entity_13_accelerate+2nd@example-platform.com'    THEN 'ENTITY_13'
                                  ELSE 'OTHER'
                              END
                            when lower(trim(Exchange_Name)) ='exchange_e' then
                             case when lower(trim (account_id)) = 'entity_03_school'                   then 'ENTITY_03'
                                  when lower(trim (account_id)) = 'entity_05_school'                   then 'ENTITY_05'
                                  when lower(trim (account_id)) = 'entity_08_main'                     then 'ENTITY_08'
                                  when lower(trim (account_id)) = 'entity_07_main'                     then 'ENTITY_07'
                                  when lower(trim (account_id)) = 'entity_13_main'                     then 'ENTITY_13'
                                  when lower(trim (account_id)) = 'entity_15_main'                     then 'ENTITY_15'
                                  when lower(trim (account_id)) = 'entity_02_main'                     then 'ENTITY_02'
                                  when lower(trim (account_id)) = 'entity_01_main'                     then 'ENTITY_01'
                                  else 'OTHER'
                              end
                        else 'OTHER'
                        end as Account_Name,
                        t.Account_Id,
                        t.invitecode as Invite_Code,
                        t.UID,
                        round(sum(t.daily_trade),2) as monthly_Trade_Vol
                from (
                 select 'Exchange_A' as exchange_name,
                        PARSE_DATE('%Y%m%d',CAST(SAFE.SUBSTR(CAST(snp_id AS STRING), 3, 8) AS STRING)) api_date,
                        lower(trim(s.account_id)) account_id,
                        lower(trim(d.invitecode)) invitecode,
                        s.uid,
                        round(( sum(tradeVol30Day)  /30),2)         daily_trade
                  from client-social-data-lake.ods.fact_exchange_a_referrals_snp s
                  inner join client-social-data-lake.ods.dim_exchange_a_accounts d on s.uid = d.uid
                  where tradeVol30Day > 0.0
                  group by snp_id, account_id, invitecode , uid
                  union all
                  select 'Exchange_B' as exchange_name,
                          m.api_date,
                          m.account_id,
                          m.inviteCode,
                          m.uid,
                          sum(tradingAmount) daily_trade
                    from  client-social-data-lake.ods.fact_exchange_b_aff_ref_snp m
                    where api_duplicate_check <2
                      and tradingAmount > 0.0
                    group by api_date,  account_id, inviteCode, uid
                    union all
                    select   'Exchange_C' as exchange_name,
                              api_date,
                              account_id,
                              '' as invitecode,
                              uid,
                              round(daily_trade,2) as daily_trade
                      from (  select  api_date,
                                      account_id,
                                      uid,
                                      sum(tradeVolume) daily_trade
                                from (  select f.api_date,
                                                d.account_id,
                                                d.uid,
                                                f.tradeVolume
                                          from client-social-data-lake.ods.fact_exchange_c_referrals_snp f
                                      left outer join client-social-data-lake.ods.dim_customer_exchange_c d
                                                  on lower(trim(f.account_id)) = lower(trim(d.account_id)) and f.uid = d.uid
                                        where tradeVolume > 0.0
                                      ) s
                                  group by api_date,
                                          account_id,
                                          uid
                            ) c
                    union all
                    select 'Exchange_D' as exchange_name,
                            api_date,
                            account_id,
                            '' as invitecode,
                            uid,
                            round(daily_trade,2) as daily_trade
                      from ( select distinct
                                    Parse_date('%Y%m%d', CAST(safe.Substr(CAST(snp_id AS STRING), 3, 8) AS STRING)) api_date,
                                    uid,
                                    sum(daily_trade_vol) daily_trade,
                                    api_email as account_id,
                                    '' as invitecode,
                               from client-social-data-lake.ods.fact_exchange_d_snp
                              group by snp_id , uid ,api_email
                           )
                    union all
                    select  'Exchange_E' as exchange_name,
                            PARSE_DATE('%Y%m%d', CAST(api_date AS STRING)) api_date,
                            account_id,
                            register_channel as inviteCode,
                            user_id as uid,
                            round(sum(futures_trading_volume) + sum(spot_trading_volume),2) daily_trade
                      from client-social-data-lake.ods.fact_exchange_e_referral_snp
                      where api_duplicate_check <2
                    group by api_date,  account_id, inviteCode, user_id
                    union all
                    select   'Exchange_F' as exchange_name,
                              PARSE_DATE('%Y%m%d', snp_date) api_date,
                              account_id,
                              inviteCode,
                              uid,
                              sum(daily_trade_vol) daily_trade
                        from (select max(snp_id) snp_id,
                                     FORMAT_DATE('%Y%m%d',snp_day) snp_date,
                                     max(year_month) year_month,
                                     max(totalTradingVolume) totalTradingVolume,
                                     round(sum(totalTradingVolume-prev_totalTradingVolume),2) as daily_trade_vol,
                                     account_id,
                                     invitecode,
                                     uid
                              from (  select max(snp_id) snp_id ,
                                             max(snp_day) snp_day,
                                             year_month,
                                             totalTradingVolume,
                                             ifnull(prev_totalTradingVolume,0.0) prev_totalTradingVolume,
                                             account_id,
                                             invitecode,
                                             uid
                                      from ( select t0.*,
                                                    t2.totalTradingVolume as prev_totalTradingVolume,
                                                from ( select t1.snp_id,
                                                              LAG(t1.snp_id) OVER (PARTITION BY t1.uid ORDER BY t1.snp_day) AS prev_snp_id,
                                                              t1.snp_day,
                                                              t1.Year_Month,
                                                              t1.totalTradingVolume,
                                                              t1.account_id,
                                                              t1.invitecode,
                                                              t1.uid
                                                        from ( with cte_1
                                                                 as (SELECT distinct
                                                                            snp_id,
                                                                            PARSE_TIMESTAMP('%Y%m%d%H%M%S', SUBSTR(CAST(snp_id AS STRING), 3, 14)) AS snp_day,
                                                                            FORMAT_DATE('%Y-%m', DATE_TRUNC(PARSE_TIMESTAMP('%Y%m%d%H%M%S', SUBSTR(CAST(snp_id AS STRING), 3, 14)), MONTH)) Year_Month,
                                                                            totalTradingVolume,
                                                                            account_id,
                                                                            uid
                                                                      FROM `client-social-data-lake.ods.fact_exchange_f_invitees_snp` )
                                                              SELECT  i.snp_id,
                                                                      i.snp_day,
                                                                      i.Year_Month,
                                                                      i.totalTradingVolume,
                                                                      i.account_id,
                                                                      c.referralcode as invitecode,
                                                                      i.uid
                                                                FROM cte_1 as i
                                                               LEFT OUTER JOIN  client-social-data-lake.ods.fact_exchange_f_commission_snp c
                                                                       ON i.account_id = c.account_id
                                                               where (i.totalTradingVolume > 0 or i.totalTradingVolume is not null)
                                                               order by 1 desc, 2 desc, 3 desc
                                                            ) t1
                                                      ) t0
                                              left outer join ( SELECT distinct
                                                                    i.snp_id,
                                                                    i.totalTradingVolume,
                                                                    i.uid
                                                                  FROM `client-social-data-lake.ods.fact_exchange_f_invitees_snp` i
                                                                ) t2 on t0.prev_snp_id = t2.snp_id and t0.uid=t2.uid
                                            )
                                            group by  year_month, totalTradingVolume,prev_totalTradingVolume, account_id, invitecode, uid
                                    ) x
                              group by FORMAT_DATE('%Y%m%d',snp_day), account_id, invitecode, uid
                      ) z
                      where daily_trade_vol > 0.0
                      group by snp_date,
                              account_id,
                              inviteCode,
                              uid
                     order by api_date desc, daily_trade desc, lower(account_id), inviteCode
                ) t
                group by Exchange_Name,Account_Name,
                        t.Account_Id, t.invitecode,t.UID,
                        FORMAT_DATE('%Y-%m', DATE_TRUNC(t.api_date, MONTH))
                ) t1
            where t1.monthly_Trade_Vol >0.0
    ) s
    ON s.Exchange_Name = t.Exchange_Name
       AND s.Year_Month = t.Year_Month
       AND s.Account_Id = t.Account_Id
       AND s.UID = t.UID
    WHEN MATCHED THEN
        UPDATE SET
            t.Account_Name     = s.Account_Name      ,
            t.Invite_Code      = s.Invite_Code       ,
            t.monthly_Trade_Vol= s.monthly_Trade_Vol ,
            t.etl_update_ts    = s.etl_update_ts
    WHEN NOT MATCHED THEN
        INSERT (Exchange_Name    ,
                Year_Month       ,
                Account_Name     ,
                Account_Id       ,
                Invite_Code      ,
                UID              ,
                monthly_Trade_Vol,
                etl_update_ts    ,
                etl_insert_ts
               )
        VALUES (s.Exchange_Name     ,
                s.Year_Month        ,
                s.Account_Name      ,
                s.Account_Id        ,
                s.Invite_Code       ,
                s.UID               ,
                s.monthly_Trade_Vol ,
                s.etl_update_ts     ,
                s.etl_insert_ts
                );

END;
