---------------1-----------

CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'audiothek_page',
  'test',
  'audiothek_page_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'audiothek_property',
  'test',
  'audiothek_property_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'audiothek_query',
  'test',
  'audiothek_query_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'audiothek_query_page',
  'test',
  'audiothek_query_page_new',
  ['SearchType'],  
  ['Date']   
);



--------2----------


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'mediathek_page',
  'test',
  'mediathek_page_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'mediathek_property',
  'test',
  'mediathek_property_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'mediathek_query',
  'test',
  'mediathek_query_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'mediathek_query_page',
  'test',
  'mediathek_query_page_new',
  ['SearchType'],  
  ['Date']   
);


 -- drop table  sep-analytics-seo-datapool.test.mediathek_page;
 alter table sep-analytics-seo-datapool.test.mediathek_page_new rename to mediathek_page;

 -- drop table  sep-analytics-seo-datapool.test.mediathek_property;
 alter table sep-analytics-seo-datapool.test.mediathek_property_new rename to mediathek_property;

 -- drop table  sep-analytics-seo-datapool.test.mediathek_query;
 alter table sep-analytics-seo-datapool.test.mediathek_query_new rename to mediathek_query;

 -- drop table  sep-analytics-seo-datapool.test.mediathek_query_page;
 alter table sep-analytics-seo-datapool.test.mediathek_query_page_new rename to mediathek_query_page;

---------3---------


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'kika_page',
  'test',
  'kika_page_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'kika_property',
  'test',
  'kika_property_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'kika_query',
  'test',
  'kika_query_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'kika_query_page',
  'test',
  'kika_query_page_new',
  ['SearchType'],  
  ['Date']   
);


 -- drop table  sep-analytics-seo-datapool.test.kika_page;
 alter table sep-analytics-seo-datapool.test.kika_page_new rename to kika_page;

 -- drop table  sep-analytics-seo-datapool.test.kika_property;
 alter table sep-analytics-seo-datapool.test.kika_property_new rename to kika_property;

 -- drop table  sep-analytics-seo-datapool.test.kika_query;
 alter table sep-analytics-seo-datapool.test.kika_query_new rename to kika_query;

 -- drop table  sep-analytics-seo-datapool.test.kika_query_page;
 alter table sep-analytics-seo-datapool.test.kika_query_page_new rename to kika_query_page;


---------4---------

CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'tagesschau_page',
  'test',
  'tagesschau_page_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'tagesschau_property',
  'test',
  'tagesschau_property_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'tagesschau_query',
  'test',
  'tagesschau_query_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'tagesschau_query_page',
  'test',
  'tagesschau_query_page_new',
  ['SearchType'],  
  ['Date']   
);


/*
drop table  sep-analytics-seo-datapool.test.tagesschau_page;
drop table  sep-analytics-seo-datapool.test.tagesschau_property;
drop table  sep-analytics-seo-datapool.test.tagesschau_query;
drop table  sep-analytics-seo-datapool.test.tagesschau_query_page;
*/

alter table sep-analytics-seo-datapool.test.tagesschau_page_new rename to tagesschau_page;
alter table sep-analytics-seo-datapool.test.tagesschau_property_new rename to tagesschau_property;
alter table sep-analytics-seo-datapool.test.tagesschau_query_new rename to tagesschau_query;
alter table sep-analytics-seo-datapool.test.tagesschau_query_page_new rename to tagesschau_query_page;



---------5---------

CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'sportschau_page',
  'test',
  'sportschau_page_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'sportschau_property',
  'test',
  'sportschau_property_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'sportschau_query',
  'test',
  'sportschau_query_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'sportschau_query_page',
  'test',
  'sportschau_query_page_new',
  ['SearchType'],  
  ['Date']   
);


/*
drop table  sep-analytics-seo-datapool.test.sportschau_page;
drop table  sep-analytics-seo-datapool.test.sportschau_property;
drop table  sep-analytics-seo-datapool.test.sportschau_query;
drop table  sep-analytics-seo-datapool.test.sportschau_query_page;
*/

alter table sep-analytics-seo-datapool.test.sportschau_page_new rename to sportschau_page;
alter table sep-analytics-seo-datapool.test.sportschau_property_new rename to sportschau_property;
alter table sep-analytics-seo-datapool.test.sportschau_query_new rename to sportschau_query;
alter table sep-analytics-seo-datapool.test.sportschau_query_page_new rename to sportschau_query_page;



---------6---------

CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'br_search_console_page',
  'test',
  'br_search_console_page_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'br_search_console_property',
  'test',
  'br_search_console_property_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'br_search_console_query',
  'test',
  'br_search_console_query_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'br_search_console_query_page',
  'test',
  'br_search_console_query_page_new',
  ['SearchType'],  
  ['Date']   
);


/*
drop table  sep-analytics-seo-datapool.test.br_search_console_page;
drop table  sep-analytics-seo-datapool.test.br_search_console_property;
drop table  sep-analytics-seo-datapool.test.br_search_console_query;
drop table  sep-analytics-seo-datapool.test.br_search_console_query_page;
*/

alter table sep-analytics-seo-datapool.test.br_search_console_page_new rename to br_search_console_page;
alter table sep-analytics-seo-datapool.test.br_search_console_property_new rename to br_search_console_property;
alter table sep-analytics-seo-datapool.test.br_search_console_query_new rename to br_search_console_query;
alter table sep-analytics-seo-datapool.test.br_search_console_query_page_new rename to br_search_console_query_page;



---------7---------

CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'ndr_search_console_page',
  'test',
  'ndr_search_console_page_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'ndr_search_console_property',
  'test',
  'ndr_search_console_property_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'ndr_search_console_query',
  'test',
  'ndr_search_console_query_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'ndr_search_console_query_page',
  'test',
  'ndr_search_console_query_page_new',
  ['SearchType'],  
  ['Date']   
);


/*
drop table  sep-analytics-seo-datapool.test.ndr_search_console_page;
drop table  sep-analytics-seo-datapool.test.ndr_search_console_property;
drop table  sep-analytics-seo-datapool.test.ndr_search_console_query;
drop table  sep-analytics-seo-datapool.test.ndr_search_console_query_page;
*/

alter table sep-analytics-seo-datapool.test.ndr_search_console_page_new rename to ndr_search_console_page;
alter table sep-analytics-seo-datapool.test.ndr_search_console_property_new rename to ndr_search_console_property;
alter table sep-analytics-seo-datapool.test.ndr_search_console_query_new rename to ndr_search_console_query;
alter table sep-analytics-seo-datapool.test.ndr_search_console_query_page_new rename to ndr_search_console_query_page;



---------8---------

CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'hr_search_console_page',
  'test',
  'hr_search_console_page_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'hr_search_console_property',
  'test',
  'hr_search_console_property_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'hr_search_console_query',
  'test',
  'hr_search_console_query_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'hr_search_console_query_page',
  'test',
  'hr_search_console_query_page_new',
  ['SearchType'],  
  ['Date']   
);


/*
drop table  sep-analytics-seo-datapool.test.hr_search_console_page;
drop table  sep-analytics-seo-datapool.test.hr_search_console_property;
drop table  sep-analytics-seo-datapool.test.hr_search_console_query;
drop table  sep-analytics-seo-datapool.test.hr_search_console_query_page;
*/

alter table sep-analytics-seo-datapool.test.hr_search_console_page_new rename to hr_search_console_page;
alter table sep-analytics-seo-datapool.test.hr_search_console_property_new rename to hr_search_console_property;
alter table sep-analytics-seo-datapool.test.hr_search_console_query_new rename to hr_search_console_query;
alter table sep-analytics-seo-datapool.test.hr_search_console_query_page_new rename to hr_search_console_query_page;




---------9---------

CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'wdr_search_console_page',
  'test',
  'wdr_search_console_page_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'wdr_search_console_property',
  'test',
  'wdr_search_console_property_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'wdr_search_console_query',
  'test',
  'wdr_search_console_query_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'wdr_search_console_query_page',
  'test',
  'wdr_search_console_query_page_new',
  ['SearchType'],  
  ['Date']   
);


/*
drop table  sep-analytics-seo-datapool.test.wdr_search_console_page;
drop table  sep-analytics-seo-datapool.test.wdr_search_console_property;
drop table  sep-analytics-seo-datapool.test.wdr_search_console_query;
drop table  sep-analytics-seo-datapool.test.wdr_search_console_query_page;
*/

alter table sep-analytics-seo-datapool.test.wdr_search_console_page_new rename to wdr_search_console_page;
alter table sep-analytics-seo-datapool.test.wdr_search_console_property_new rename to wdr_search_console_property;
alter table sep-analytics-seo-datapool.test.wdr_search_console_query_new rename to wdr_search_console_query;
alter table sep-analytics-seo-datapool.test.wdr_search_console_query_page_new rename to wdr_search_console_query_page;



---------10---------

CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'swr_search_console_page',
  'test',
  'swr_search_console_page_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'swr_search_console_property',
  'test',
  'swr_search_console_property_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'swr_search_console_query',
  'test',
  'swr_search_console_query_new',
  ['SearchType'],  
  ['Date']   
);


CALL `sep-analytics-seo-datapool.tmp.prc_partition_table`(
  'test',
  'swr_search_console_query_page',
  'test',
  'swr_search_console_query_page_new',
  ['SearchType'],  
  ['Date']   
);


/*
drop table  sep-analytics-seo-datapool.test.swr_search_console_page;
drop table  sep-analytics-seo-datapool.test.swr_search_console_property;
drop table  sep-analytics-seo-datapool.test.swr_search_console_query;
drop table  sep-analytics-seo-datapool.test.swr_search_console_query_page;
*/

alter table sep-analytics-seo-datapool.test.swr_search_console_page_new rename to swr_search_console_page;
alter table sep-analytics-seo-datapool.test.swr_search_console_property_new rename to swr_search_console_property;
alter table sep-analytics-seo-datapool.test.swr_search_console_query_new rename to swr_search_console_query;
alter table sep-analytics-seo-datapool.test.swr_search_console_query_page_new rename to swr_search_console_query_page;












