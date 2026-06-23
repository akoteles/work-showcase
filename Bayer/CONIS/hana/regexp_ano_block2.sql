DO
 BEGIN
	declare v_occurrences integer;
    declare v_out         varchar(20);
	declare v_output      varchar(1000);
	declare v_exists      integer;
    declare i             integer = 0;
    declare
     CURSOR c_main (v_occ_offset integer) FOR
	  SELECT substring_regexpr('\b\w{5,}+(?<!input)\b' FLAG 'i' in t.txt
	                           FROM LOCATE_REGEXPR('(input)' FLAG 'i' in t.txt
	                                               OCCURRENCE  OCCURRENCES_REGEXPR('(input)' FLAG 'i' in t.txt)-(:v_occ_offset-1)
	                                              )
	                           ) v_regexpr
	    FROM (Select compilation_rule as txt FROM SOURCE_SYSTEM_A_OP.ETL_COMPILATION_RULE
	         ) t;


	  SELECT OCCURRENCES_REGEXPR('(input)' FLAG 'i' in t.txt)  into  v_occurrences
	    FROM (Select compilation_rule as txt FROM SOURCE_SYSTEM_A_OP.ETL_COMPILATION_RULE
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

			OPEN  c_main(:v_occurrences-:i);
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

		SELECT 'out: '||v_output FROM dummy;

		SELECT distinct val FROM #TEMP_DISTINCT_VALUES;
		drop table #TEMP_DISTINCT_VALUES;
END;
