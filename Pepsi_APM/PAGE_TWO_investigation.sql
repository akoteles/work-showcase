SELECT *
  FROM planning_schema_DATA_DICTIONARY
 WHERE src_table = 'PAGE_TWO';




select * from mds.BI_DATA_DICTIONARY

select * from BI_DATA_DICTIONARY where src_table like '%PAGE%'

select * from BI_DATA_DICTIONARY where tgt_table like '%PAGE%'


 select * from planning_schema_DATA_DICTIONARY where tgt_table like '%PAGE%'

create table test1 as
  select
         tw.id,
          tw.text03         ,
         tw.text01         ,
         tw.text13         ,
         tw.text14         ,
         tw.list75         ,
         tw.text04         ,
         tw.list03         ,
         tw.list01         ,
         tw.list02         ,
         tw.list12         ,
         tw.text12         ,
         tw.create_user    ,
         tw.list15         ,
         tw.list17         ,
         tw.list16         ,
         tw.list08         ,
         tw.list04         ,
         tw.list10         ,
         tw.list20         ,
         tw.text16         ,
         tw.list23         ,
         tw.list21         ,
         tw.list22         ,
         tw.list09         ,
         tw.list05         ,
         tw.list25         ,
         tw.list24         ,
         tw.list18         ,
         tw.list19         ,
         tw.list66         ,
         tw.list67         ,
         tw.list69         ,
         tw.text18         ,
         tw.text23         ,
         tw.text06         ,
         tw.text66         ,
         tw.text09         ,
         tw.list71         ,
         tw.list72         ,
         tw.list73         ,
         tw.list68         ,
         tw.list70         ,
         tw.list07         ,
         tw.list06         ,
         tw.list13         ,
         tw.text15         ,
         tw.list76         ,
         tw.text02         ,
         tw.list14         ,
         tw.text10         ,
                 tw.list11       ,
         tw.created,
         tw.last_upd
    from PAGE_TWO@OPLM1D tw
    where 1=2;


SELECT *
  FROM (SELECT column_name
          FROM user_tab_cols
         WHERE table_name = 'TEST1') a
       LEFT OUTER JOIN (SELECT DISTINCT src_col
                          FROM planning_schema_DATA_DICTIONARY
                         WHERE src_table = 'PAGE_TWO') b
          ON a.column_name = b.src_col;



drop table test1 purge;
