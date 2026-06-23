


select * from all_db_links


select * from dual@OPLM1D


select * from etl_run_info order by 1 desc



    select * from PAGE_TWO@OPLM1D order by created desc, last_upd desc


    select * from PAGE_THREE@OPLM1D order by created desc, last_upd desc


    select * from all_source  where lower(text) like '%page_two%'


    select * from all_source  where upper(text) like '%MDS_PAGE_TWO%'

