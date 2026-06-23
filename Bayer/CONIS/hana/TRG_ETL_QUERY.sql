Drop  trigger TRG_ETL_QUERY;
CREATE TRIGGER SOURCE_SYSTEM_A_OP.TRG_ETL_QUERY BEFORE
INSERT or UPDATE ON SOURCE_SYSTEM_A_OP.ETL_QUERY REFERENCING NEW ROW MYNEWROW
 FOR EACH ROW
 BEGIN
	 declare  v_new integer;
	 declare  v_max integer;

	    if (:MYNEWROW.PROCESS_NAME is not null and :MYNEWROW.QUERY_ID = 0 ) or :MYNEWROW.QUERY_ID is null
	    then

	    	DECLARE CURSOR c_main (v_system_id integer, v_process_name varchar(100))
	    	FOR
	    	 select * from (
	       	    Select max(query_id) query_id, SYSTEM_ID
	       	      from SOURCE_SYSTEM_A_OP.ETL_QUERY
	       	     Where SYSTEM_ID = v_system_id
				   and process_name = v_process_name
	       	     Group by SYSTEM_ID
	       	     union all
	       	    select -1,-1 from dummy
	       		 ORDER BY 2 desc
	       		)  limit 1;

			FOR i AS c_main(:MYNEWROW.SYSTEM_ID, :MYNEWROW.PROCESS_NAME)
			DO
				select IFNULL(max(query_id),0) into v_new from SOURCE_SYSTEM_A_OP.ETL_QUERY where process_name = :MYNEWROW.PROCESS_NAME;

				if i.query_id = v_new then
					MYNEWROW.QUERY_ID = i.query_id;

				elseif i.query_id = -1 then
			     select IFNULL(max(query_id),0) into v_max from SOURCE_SYSTEM_A_OP.ETL_QUERY;
			     MYNEWROW.QUERY_ID = v_max+1;

			    elseif i.query_id > 0 then
			    	select IFNULL(max(query_id),0) into v_max from SOURCE_SYSTEM_A_OP.ETL_QUERY;
			    	select IFNULL(max(query_id),0) into v_new from SOURCE_SYSTEM_A_OP.ETL_QUERY where process_name = :MYNEWROW.PROCESS_NAME;

			    	if v_new < i.query_id  then
			    		MYNEWROW.QUERY_ID = v_max+1;
			        end if;

			    end if;
			END FOR;
		end if;
end;
