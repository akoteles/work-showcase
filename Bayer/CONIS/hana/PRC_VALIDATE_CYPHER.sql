drop PROCEDURE  SOURCE_SYSTEM_A_OP."PRC_VALIDATE_CYPHER";

CREATE PROCEDURE  SOURCE_SYSTEM_A_OP."PRC_VALIDATE_CYPHER"
(IN  I_RULE_ID     INTEGER,
 OUT OUTPUT_TABLE  SOURCE_SYSTEM_A_OP."TEMP_DISTINCT_VALUES" )
           LANGUAGE SQLSCRIPT
           SQL SECURITY INVOKER
           AS
BEGIN
	declare v_occurrences integer;
	declare v_rule_id     integer;
    declare v_out         varchar(100);
	declare v_output      varchar(5000);
	declare v_exists      integer;
    declare i             integer = 0;
    declare
     CURSOR c_main (v_occ_offset integer, v_i_rule_id integer) FOR
	  SELECT substring_regexpr('\b\w{4,}+(?<!input)\b' FLAG 'i' in t.txt
	                           FROM LOCATE_REGEXPR('(input)' FLAG 'i' in t.txt
	                                               OCCURRENCE  OCCURRENCES_REGEXPR('(input)' FLAG 'i' in t.txt)-(:v_occ_offset-1)
	                                              )
	                           ) v_regexpr
	    FROM (Select compilation_rule as txt FROM SOURCE_SYSTEM_A_OP.ETL_HARMONIZED_COMPILATION_RULE where RULE_ID = :v_i_rule_id
	         ) t;


	  v_rule_id = :I_RULE_ID;

	  SELECT OCCURRENCES_REGEXPR('(input)' FLAG 'i' in t.txt)  into  v_occurrences
	    FROM (Select compilation_rule as txt FROM SOURCE_SYSTEM_A_OP.ETL_HARMONIZED_COMPILATION_RULE where RULE_ID = :I_RULE_ID
			  ) t ;

       select max(val)
         into v_exists
         from (
		       select distinct 1 val from M_TEMPORARY_TABLES
		        where  schema_name ='SOURCE_SYSTEM_A_OP' and table_name  = '#TEMP_DISTINCT_VALUES' and IS_TEMPORARY = 'TRUE'
		        union all
		       select 0 from dummy
             );

        if v_exists = 1 then
        	begin
        		drop table #TEMP_DISTINCT_VALUES;
        	end;
        end if;

        create local temporary table #TEMP_DISTINCT_VALUES ( val varchar(100));

		WHILE :i < v_occurrences DO

			OPEN  c_main(:v_occurrences-:i,:I_RULE_ID);
			FETCH c_main INTO v_out;
			CLOSE c_main;

            if :v_output is null then
				v_output := v_out;
				insert into #TEMP_DISTINCT_VALUES values (v_out);
		    else
		    	v_output := v_output|| ','||BINTOSTR( HEXTOBIN('0D0A') )||v_out;

		    	insert into #TEMP_DISTINCT_VALUES values (v_out);
		    end if;

			i = :i + 1;
		END WHILE;

	    OUTPUT_TABLE =SELECT distinct val FROM #TEMP_DISTINCT_VALUES;
		drop table #TEMP_DISTINCT_VALUES;
END;




  do
  begin
    declare vOUTPUT_TABLE SOURCE_SYSTEM_A_OP.TEMP_DISTINCT_VALUES;
    call SOURCE_SYSTEM_A_OP."PRC_VALIDATE_CYPHER"(1,vOUTPUT_TABLE);


		SELECT * FROM :vOUTPUT_TABLE;
  end;
