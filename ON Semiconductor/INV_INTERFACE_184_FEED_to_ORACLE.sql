        select * from XXCLIENT_ORDER_FEED_STG where batch_id=6447562

        select * from XXCLIENT_ORDER_FEED_STG where cust_prod_name ='CUST_PROD_001';

        select * from XXCLIENT_ORDER_FEED_MASTER_STG where customer_cd ='CUST_PROD_001';

        select * from XXCLIENT_ORDER_TARGET_STG order by last_updated_date desc

         select * from XXCLIENT_ORDER_FEED_MASTER_STG  order by last_updated_date desc;



        SELECT count(1),batch_id
            FROM XXCLIENT_ORDER_FEED_STG
      group by batch_id


        select count(1),cust_prod_name from XXCLIENT_ORDER_FEED_STG where cust_prod_name ='CUST_PROD_001' group by cust_prod_name

        select count(1),batch_id,REGION_CD from XXCLIENT_ORDER_FEED_STG group by batch_id,REGION_CD

        select count(1),batch_id from XXCLIENT_ORDER_FEED_STG group by batch_id

        select count(1),batch_id from XXCLIENT_ORDER_FEED_MASTER_STG group by batch_id

        select count(1),file_id from XXCLIENT_ORDER_TARGET_STG group by file_id


            select * from  XXCLIENT_ORDER_FEED_MASTER_STG  where  document_num = '178389';

         select * from XXCLIENT_ORDER_FEED_MASTER_STG where batch_id=5854706 and document_num=40233  order by last_updated_date desc;

         select * from XXCLIENT_ORDER_TARGET_STG where file_id=5854706 and cm_sales_order=265447 order by last_updated_date desc


                    SELECT *
                      FROM xxclient_order_feed_stg
                     WHERE     document_num NOT IN (SELECT DISTINCT cm_sales_order
                                                      FROM xxclient_order_target_stg)
                           AND document_num NOT IN (SELECT DISTINCT document_num
                                                      FROM XXCLIENT_ORDER_FEED_MASTER_STG)


                        select * from client_etl_log order by 1 desc;

                        select * from CLIENT_EBS_CONTROL;


                            select * from XXCLIENT_ORDER_FEED_MASTER_STG  where batch_id=5854706 order by last_updated_date desc;

                            select * from XXCLIENT_ORDER_FEED_MASTER_STG

                            select * from XXCLIENT_ORDER_TARGET_STG where file_id=5854706  order by last_updated_date desc;


                                        select * from xxclient.XXCLIENT_ORDER_FEED_DATE_COMPARE

                                        select * from xxclient.XXCLIENT_ORDER_FEED_COMPARE



                                UPDATE FND_LOOKUP_VALUES
                                set DESCRIPTION = 6447591
                                where LOOKUP_TYPE = 'XXCLIENT_ORDER_FEED_REGION_BATCH_CODES' and language='US' and LOOKUP_CODE in ('JO');

                                commit;

                                    update XXCLIENT_ORDER_FEED_STG
                                    set status = 'NEW', batch_id = 6447591
                                    where batch_id  in (6447590)
                                      and customer_cd ='CUST_001' and document_num = 268883
                                      ;

                                    commit;


                           BEGIN
                           XXCLIENT_ORDER_FEED_DATA_LOAD_PKG.FEED_MAIN_LOAD;
                           END;


select * from client_etl_log order by 1 desc

select * from XXCLIENT_ORDER_FEED_REGION_BATCH_CODES;

select * from FND_LOOKUP_VALUES where LOOKUP_TYPE = 'XXCLIENT_ORDER_FEED_REGION_BATCH_CODES' and language='US'



                         select count(1),batch_id from XXCLIENT_ORDER_FEED_MASTER_STG  group by batch_id order by 2


                                commit;


CHANGE  361500914    FEED_DATE_MATCH
  null  361500915    FEED_DATE_EXISTS

null 361500914    FEED_DATE_MATCH
add  361500915    FEED_DATE_EXISTS


    begin
        UPDATE XXCLIENT_ORDER_FEED_REGION_BATCH_CODES
        SET END_DATE = NULL
        WHERE END_DATE IS NOT NULL;
        COMMIT;

      XXCLIENT_ORDER_FEED_DATA_LOAD_PKG.FEED_MAIN_LOAD;
    end;



select * from FND_LOOKUP_VALUES where LOOKUP_TYPE = 'XXCLIENT_ORDER_FEED_REGION_BATCH_CODES' and language='US'

        UPDATE FND_LOOKUP_VALUES
        set DESCRIPTION = 6447572
        where LOOKUP_TYPE = 'XXCLIENT_ORDER_FEED_REGION_BATCH_CODES' and language='US' and LOOKUP_CODE in ('JO');

       COMMIT;



    BEGIN

        XXCLIENT_ORDER_FEED_DATA_LOAD_PKG.FEED_MAIN_LOAD;

    END;


        select count(1),batch_id,region_cd from XXCLIENT_ORDER_FEED_STG where batch_id > 33333
         group by batch_id, region_cd order by 1 desc


        SELECT DISTINCT
                   f.REGION_CD,
                   f.BATCH_ID,
                   lk.DESCRIPTION as LAST_BATCH_ID
              FROM XXCLIENT_ORDER_FEED_STG f
        LEFT OUTER JOIN FND_LOOKUP_VALUES lk ON f.REGION_CD=lk.LOOKUP_CODE AND (LANGUAGE = 'US' AND LOOKUP_TYPE = 'XXCLIENT_ORDER_FEED_REGION_BATCH_CODES')
             WHERE f.BATCH_ID > 6447562
               AND f.REGION_CD = 'JO'



    declare
       v_err_code   VARCHAR2(100);
       v_err_msg    VARCHAR2(1000);
    begin
        XXCLIENT_ORDER_FEED_DATA_LOAD_PKG.FEED_DATA_LOAD ( v_err_code,v_err_msg ,'EO',5854706 );
        if v_err_code is not null or v_err_msg is not null then
        dbms_output.put_line (v_err_code || ' -> msg: '|| v_err_msg );
        else
            null;
        end if;
    END;


select * from xxclient.XXCLIENT_ORDER_FEED_PRICE_STG

select * from XXCLIENT_ORDER_FEED_MASTER_STG

select * from XXCLIENT_ORDER_FEED_MASTER_STG order by last_updated_date desc

select * from client_etl_log order by 1 desc;

    select * from client_etl_log where log_short_text like '%FEED_3%' order by 1 desc;



select * from XXCLIENT_ORDER_FEED_REGION_BATCH_CODES;

                select * from XXCLIENT_ORDER_FEED_REGION_BATCH_CODES as of timestamp sysdate-1/24;

select * from FND_LOOKUP_VALUES where LOOKUP_TYPE = 'XXCLIENT_ORDER_FEED_REGION_BATCH_CODES' and language='US'



        select * from XXCLIENT_ORDER_FEED_STG where batch_id=6447563

select * from CLIENT_EBS_CONTROL


                                select * from all_source where owner='APPS' and name like 'XXCLIENT%' and type like '%PACKAG%'
                                and lower(text) like '%batch%'

                                SELECT *
                                  FROM all_source
                                 WHERE     name IN (SELECT DISTINCT name
                                                      FROM all_source
                                                     WHERE     owner = 'APPS'
                                                           AND NAME LIKE 'XXCLIENT%'
                                                           AND TYPE LIKE '%PACKAG%'
                                                           AND LOWER (text) LIKE '%fnd_lookup%')
                                       AND LOWER (text) LIKE '%batch%'

    SHIP-TO-CUST-CODE + PROD-NAME + CUST-PROD-NAME


SELECT DISTINCT
       SHIP_TO_CUSTOMER_C AS SHIP_TO_CUSTOMER_CODE,
       PART_ID AS PROD_NAME,
       CUST_PROD_NAME
  FROM XXCLIENT_ORDER_FEED_STG


select * from XXCLIENT_ORDER_TARGET_STG order by cr_accounting_period desc;

   select * from XXCLIENT_ORDER_TARGET_STG where CR_BOOKING_AND_BILLIN = 'ADD';

select * from xxclient_order_feed_stg;

select * from XXCLIENT_ORDER_FEED_MASTER_STG;


         select * from xxclient_order_feed_stg where SHIP_TO_CUSTOMER_C='CUST_001' and part_id='PART_EXAMPLE_001' and cust_prod_name='CUST_PROD_001'

          SELECT DISTINCT
               SHIP_TO_CUSTOMER_C AS SHIP_TO_CUSTOMER_CODE,
               PART_ID AS PROD_NAME,
               CUST_PROD_NAME
          FROM XXCLIENT_ORDER_FEED_STG
         WHERE REGION_CD = p_region_cd
           AND SHIP_TO_CUSTOMER_C='CUST_002' and part_id='PART_EXAMPLE_002' and cust_prod_name='CUST_PROD_002'


         select * from xxclient_order_feed_stg where row_id in (361500914,361500915)

                select * from xxclient_order_feed_stg where row_id in (select row_id from XXCLIENT_ORDER_FEED_MASTER_STG );


SET DEFINE OFF;
Insert into APPS.XXCLIENT_ORDER_FEED_STG
   (ROW_ID, CUSTOMER_CD, PART_ID, CUST_PROD_NAME, CRD,
    REGION_CD, HANDLING_CD, ORDER_TYPE_CD, DELIVERY_NUM, QTY,
    MSD, DOCUMENT_NUM, SO_ITM_NUM, UNIT_PRICE, SALES_ORDER_REGION,
    SHIP_TO_CUSTOMER_C, SOLD_TO_CUSTOMER_C, SO_PRC_SOURCE, SO_TRANSIT_DAYS, BATCH_ID,
    STATUS, CURRENCY, CREATION_DATE, CREADTED_BY, LAST_UPDATE_DATE,
    LAST_UPDATE_BY)
 Values
   (1, '9001', '1005', '20001', TO_DATE('04/10/2017 00:00:00', 'MM/DD/YYYY HH24:MI:SS'),
    'US', 'XX', 'XX', 9999, 5,
    TO_DATE('04/10/2017 00:00:00', 'MM/DD/YYYY HH24:MI:SS'), 501, 111, 100.99, 'US',
    '19001', '19001', 'F', 12, 9999,
    'FEED_NEW', 'USD', TO_DATE('04/11/2017 00:00:00', 'MM/DD/YYYY HH24:MI:SS'), 'XXX', TO_DATE('04/10/2017 00:00:00', 'MM/DD/YYYY HH24:MI:SS'),
    'XXX');

Insert into APPS.XXCLIENT_ORDER_FEED_STG
   (ROW_ID, CUSTOMER_CD, PART_ID, CUST_PROD_NAME, CRD,
    REGION_CD, HANDLING_CD, ORDER_TYPE_CD, DELIVERY_NUM, QTY,
    MSD, DOCUMENT_NUM, SO_ITM_NUM, UNIT_PRICE, SALES_ORDER_REGION,
    SHIP_TO_CUSTOMER_C, SOLD_TO_CUSTOMER_C, SO_PRC_SOURCE, SO_TRANSIT_DAYS, BATCH_ID,
    STATUS, CURRENCY, CREATION_DATE, CREADTED_BY, LAST_UPDATE_DATE,
    LAST_UPDATE_BY)
 Values
   (1, '9002', '1007', '20002', TO_DATE('04/10/2017 00:00:00', 'MM/DD/YYYY HH24:MI:SS'),
    'US', 'XX', 'XX', 9990, 15,
    TO_DATE('04/10/2017 00:00:00', 'MM/DD/YYYY HH24:MI:SS'), 401, 111, 12.01, 'US',
    '19001', '19001', 'F', 12, 9999,
    'FEED_NEW', 'USD', TO_DATE('04/10/2017 00:00:00', 'MM/DD/YYYY HH24:MI:SS'), 'XXX', TO_DATE('04/10/2017 00:00:00', 'MM/DD/YYYY HH24:MI:SS'),
    'XXX');

COMMIT;


 delete from XXCLIENT_ORDER_FEED_STG where ROW_ID =361500915 ; commit;

SET DEFINE OFF;
Insert into APPS.XXCLIENT_ORDER_FEED_STG
   (ROW_ID, CUSTOMER_CD, PART_ID, CUST_PROD_NAME, CRD,
    REGION_CD, HANDLING_CD, ORDER_TYPE_CD, DELIVERY_NUM, QTY,
    MSD, DOCUMENT_NUM, SO_ITM_NUM, UNIT_PRICE, SALES_ORDER_REGION,
    SHIP_TO_CUSTOMER_C, SOLD_TO_CUSTOMER_C, SO_PRC_SOURCE, SO_TRANSIT_DAYS, BATCH_ID,
    STATUS, CURRENCY, CREATION_DATE, CREADTED_BY, LAST_UPDATE_DATE,
    LAST_UPDATE_BY, CUS_PURCHASE_AGREE, OM_PRICE)
 Values
   (361500915, 'CUST_002', 'PART_EXAMPLE_002', 'CUST_PROD_002', TO_DATE('04/11/2017 00:00:00', 'MM/DD/YYYY HH24:MI:SS'),
    'EO', 'B', 'F', 7, 25710,
    TO_DATE('03/17/2017 00:00:00', 'MM/DD/YYYY HH24:MI:SS'), 162406, 1, 27200, 'EO      ',
    'CUST_002', 'CUST_002', 'A', 5, 5854706,
    NULL, NULL, TO_DATE('04/11/2017 05:32:20', 'MM/DD/YYYY HH24:MI:SS'), '-1', TO_DATE('04/11/2017 05:32:20', 'MM/DD/YYYY HH24:MI:SS'),
    '-1', NULL, 12542);
COMMIT;


  SELECT MAX(V_FOUND) V_FOUND
              FROM (SELECT '1' V_FOUND
                      FROM XXCLIENT_ORDER_FEED_MASTER_STG
                    UNION ALL
                    SELECT '0' FROM DUAL )


 SELECT DISTINCT
                   SHIP_TO_CUSTOMER_C AS SHIP_TO_CUSTOMER_CODE,
                   PART_ID AS PROD_NAME,
                   CUST_PROD_NAME,
                   CRD
              FROM XXCLIENT_ORDER_FEED_STG
              where SHIP_TO_CUSTOMER_C='CUST_002' and part_id='PART_EXAMPLE_002' and cust_prod_name='CUST_PROD_002'
              ;



              select * from XXCLIENT_ORDER_FEED_STG;



                  MERGE
             INTO XXCLIENT_ORDER_FEED_COMPARE t
            USING ( SELECT
                          m.CUSTOMER_CD   ,
                          m.PART_ID       ,
                          m.CUST_PROD_NAME
                     FROM XXCLIENT_ORDER_FEED_MASTER_STG m
                    WHERE NOT EXISTS ( SELECT  1
                                         FROM  XXCLIENT_ORDER_FEED_STG s
                                        WHERE s.SHIP_TO_CUSTOMER_C = m.CUSTOMER_CD
                                          AND s.PART_ID            = m.PART_ID
                                          AND s.CUST_PROD_NAME     = m.CUST_PROD_NAME
                                      )
                      AND m.CUSTOMER_CD    = 'CUST_002'
                      AND m.PART_ID        = 'PART_EXAMPLE_002'
                      AND m.CUST_PROD_NAME = 'CUST_PROD_002'
                  ) s
               ON (    t.SHIP_TO_CUSTOMER_CODE = s.CUSTOMER_CD
                   AND t.PROD_NAME             = s.PART_ID
                   AND t.CUST_PROD_NAME        = s.CUST_PROD_NAME )
             WHEN MATCHED THEN
               UPDATE
                  SET STATUS = 'FEED_DELETE'
             WHEN NOT MATCHED THEN
               INSERT ( SHIP_TO_CUSTOMER_CODE,
                        PROD_NAME,
                        CUST_PROD_NAME,
                        STATUS )
               VALUES ( s.CUSTOMER_CD,
                        s.PART_ID,
                        s.CUST_PROD_NAME,
                        'FEED_DELETE');




         SELECT
                m.CUSTOMER_CD,
                m.PART_ID,
                m.CUST_PROD_NAME,
                m.CRD
          FROM XXCLIENT_ORDER_FEED_MASTER_STG m
         WHERE (    SHIP_TO_CUSTOMER_C =  'CUST_002'
                AND PART_ID            =  'PART_EXAMPLE_002'
                AND CUST_PROD_NAME     =  'CUST_PROD_002'   )
           AND STATUS NOT IN ( 'MASTER_DATE_EXISTS','DELETE')
           AND NOT EXISTS (SELECT  1
                             FROM  (SELECT
                                           c.SHIP_TO_CUSTOMER_CODE,
                                           c.PROD_NAME            ,
                                           c.CUST_PROD_NAME       ,
                                           s.CRD
                                      FROM XXCLIENT_ORDER_FEED_COMPARE c
                                     INNER JOIN XXCLIENT_ORDER_FEED_STG s
                                        ON    (c.SHIP_TO_CUSTOMER_CODE = s.SHIP_TO_CUSTOMER_C
                                           AND c.PROD_NAME             = s.PART_ID
                                           AND c.CUST_PROD_NAME        = s.CUST_PROD_NAME )
                                      ) t
                            WHERE  t.SHIP_TO_CUSTOMER_CODE = m.CUSTOMER_CD
                              AND  t.PROD_NAME             = m.PART_ID
                              AND  t.CUST_PROD_NAME        = m.CUST_PROD_NAME
                              AND  t.CRD                   = m.CRD);


          select count(1),region_cd,batch_id from XXCLIENT_ORDER_FEED_MASTER_STG group by region_cd,batch_id;


          select count(1),cm_so_region,file_id from XXCLIENT_ORDER_TARGET_STG group by cm_so_region,file_id;


          select count(1),status,file_id from XXCLIENT_ORDER_TARGET_STG group by status,file_id;

          select count(1),status,batch_id from XXCLIENT_ORDER_FEED_MASTER_STG group by status,batch_id;
