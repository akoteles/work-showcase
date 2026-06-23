select * from xxclient.XXCLIENT_ORDER_FEED_PRICE_STG


        select * from XXCLIENT_ORDER_FEED_STG where  batch_id=6447562 and cust_prod_name='CUST_PROD_001'


        select * from XXCLIENT_ORDER_FEED_MASTER_STG where
        cust_prod_name='CUST_PROD_001' and customer_cd ='CUST_001'
        order by last_update_date desc


        select *  FROM "XXCLIENT"."XXCLIENT_ORDER_FEED_MASTER_STG";



        UPDATE XXCLIENT_ORDER_FEED_MASTER_STG
           set batch_id =6447561
        where batch_id=11111 and
        cust_prod_name='CUST_PROD_001';

        commit;



        select * from XXCLIENT_ORDER_TARGET_STG where  file_id=6447562 and cr_product_name='PART_EXAMPLE_001'



        select * from XXCLIENT_ORDER_FEED_STG order by last_updated_date desc


        select * from XXCLIENT_ORDER_FEED_MASTER_STG order by last_updated_date desc


        select * from XXCLIENT_ORDER_FEED_COMPARE



        select t.*
                      from XXCLIENT_ORDER_FEED_STG t
                     where exists (  select 1
                                       from XXCLIENT_ORDER_FEED_COMPARE s1
                                      where t.CUSTOMER_CD    = s1.SHIP_TO_CUSTOMER_CODE
                                        and t.PART_ID        = s1.PROD_NAME
                                        and t.CUST_PROD_NAME = s1.CUST_PROD_NAME
                                        and t.batch_id       = 6447562 )
                       and not exists
                                  ( select 1
                                       from XXCLIENT_ORDER_FEED_MASTER_STG m
                                      where t.CUSTOMER_CD    = m.CUSTOMER_CD
                                        and t.PART_ID        = m.PART_ID
                                        and t.CUST_PROD_NAME = m.CUST_PROD_NAME
                                        and t.batch_id       = m.batch_id )
                       and t.cust_prod_name ='CUST_PROD_001'


select t.*
                      from XXCLIENT_ORDER_FEED_STG t
                     where exists (  select 1
                                       from XXCLIENT_ORDER_FEED_DATE_COMPARE s1
                                      where
                                            t.CUSTOMER_CD    = s1.SHIP_TO_CUSTOMER_CODE
                                        and t.PART_ID        = s1.PROD_NAME
                                        and t.CUST_PROD_NAME = s1.CUST_PROD_NAME
                                        and t.CRD            = s1.CRD )
                       and t.cust_prod_name ='CUST_PROD_001'


select t.SHIP_TO_CUSTOMER_CODE,
                           t.PROD_NAME,
                           t.CUST_PROD_NAME,
                           f.OM_PRICE
                      from XXCLIENT_ORDER_FEED_COMPARE t
                left outer join XXCLIENT_ORDER_FEED_STG f on (      f.CUSTOMER_CD    = t.SHIP_TO_CUSTOMER_CODE
                                                        and f.PART_ID        = t.PROD_NAME
                                                        and f.CUST_PROD_NAME = t.CUST_PROD_NAME  )
                     where t.status like '%DELETE%'
                       and not exists (  select 1
                                       from XXCLIENT_ORDER_FEED_MASTER_STG s
                                      where    (t.SHIP_TO_CUSTOMER_CODE    = s.CUSTOMER_CD
                                            and t.PROD_NAME                = s.PART_ID
                                            and t.CUST_PROD_NAME           = s.CUST_PROD_NAME )
                                        and s.status not like '%DELETE%'
                                      )
                       and f.cust_prod_name ='CUST_PROD_001'
