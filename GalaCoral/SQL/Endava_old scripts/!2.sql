


select distinct
       AR_ITEM_ID
       ,ITEM_REF
       ,AR_ITEM_TYPE
       ,CUSTOMER_CONTRACT_ID
       ,FIRST_CONTRACT_ITEM_IND
       ,CURRENCY_CODE
       ,sum(TOTAL_AMOUNT) over (partition by item_ref,customer_ref,creation_date) TOTAL_AMOUNT
       ,sum(REMAINING_BALANCE_AMOUNT) over (partition by item_ref,customer_ref,creation_date) REMAINING_BALANCE_AMOUNT
       ,TAX_AMOUNT
       ,TAX_RECHARGE_INDICATOR
       ,case
        when sum(TOTAL_AMOUNT) over (partition by item_ref,customer_ref,creation_date) >= 0 then 'D'
          else 'C'
      end DEBIT_OR_CREDIT
       ,CREATION_DATE
       ,CAPTURED_DATE
       ,DUE_DATE
       ,RAISED_BY
       ,AUTHORISATED_BY
       ,MANUAL_INVOICE_TYPE
       ,IN_DISPUTE_IND
       ,CLAIM_ID
       ,CLAIM_VERSION
       ,CLAIM_INVOICE_NO
       ,ACCOUNTING_DONE
       ,WRITE_OFF_TYPE
       ,AR_ITEM_ADJUSTMENT_REASON_CODE
       ,ADJUSTED_AR_ITEM
       ,AUTHORIZATION_CODE
       ,AUTHORIZATION_EXP_DATE
       ,CUSTOMER_REF
       ,SUBCUST_QUAL2
       ,ACCOUNTING_DT
     from stg_ar_items where  (item_ref,customer_ref,creation_date) in (
     select item_ref,customer_ref,creation_date from stg_ar_items i
     group by (item_ref,customer_ref,creation_date)
     having count(1) > 1



     desc dbms_rlmgr_dr.execschdactions;

   desc X$DUAL;

  select * from v$fixed_table where name like '%DUAL%';


  desc v%sgastat
  show parameters area_size



select to_char(sysdate,'mm-dd-yyyy hh24:mi:ss'),pool, name, bytes/(1024*1024)
from v$sgastat, dual
where name = 'free memory' order by bytes asc
;


select pool ,sum(bytes) from v$sgastat
group by pool;

ALTER SYSTEM FLUSH SHARED_POOL;
ALTER SYSTEM FLUSH BUFFER_CACHE;


select to_char(sysdate,'mm-dd-yyyy hh24:mi:ss'), name, bytes/(1024*1024)
from v$sgastat where name like '%buffer%';




select
    to_char(ssn.sid, '9999') || ' - ' || nvl(ssn.username,
    nvl(bgp.name, 'background')) || nvl(lower(ssn.machine), ins.host_name) ssession,
    to_char(prc.spid, '999999999')                       pid_thread,
    to_char((se1.value / 1024) / 1024, '999g999g990d00') current_size_mb,
    to_char((se2.value / 1024) / 1024, '999g999g990d00') maximum_size_mb
from
    v$statname  stat1,
    v$statname  stat2,
    v$session   ssn,
    v$sesstat   se1,
    v$sesstat   se2,
    v$bgprocess bgp,
    v$process   prc,
    v$instance  ins
where
    stat1.name = 'session pga memory'
and
    stat2.name = 'session pga memory max'
and
    se1.sid = ssn.sid
and
    se2.sid = ssn.sid
and
    se2.statistic# = stat2.statistic#
and
    se1.statistic# = stat1.statistic#
and
    ssn.paddr = bgp.paddr(+)
and
    ssn.paddr = prc.addr(+);
