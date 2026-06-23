DO
 BEGIN
	declare v_occurrences integer;
    declare v_out         varchar(20);
	declare v_output      varchar(1000);
    declare i             integer = 0;
    declare CURSOR c_main (v_occ_offset integer) FOR
			  SELECT substring_regexpr('\b\w+(?<!input)\b' FLAG 'i' in t.txt
			                           FROM LOCATE_REGEXPR('\b\w+[input]\b' FLAG 'i' in t.txt
			                                               OCCURRENCE  OCCURRENCES_REGEXPR('\b\w+[input]\b' FLAG 'i' in t.txt)-(:v_occ_offset-1)
			                                              )
			                           ) v_regexpr
			    FROM (Select compilation_rule as txt FROM SOURCE_SYSTEM_A_OP.ETL_COMPILATION_RULE
			         ) t;


	  SELECT OCCURRENCES_REGEXPR('\b\w+[input]\b' FLAG 'i' in t.txt)  into  v_occurrences
	    FROM (Select compilation_rule as txt FROM SOURCE_SYSTEM_A_OP.ETL_COMPILATION_RULE
			  ) t ;

		SELECT v_occurrences FROM dummy;

		WHILE :i < v_occurrences DO

			OPEN  c_main(:v_occurrences-:i);
			FETCH c_main INTO v_out;
			CLOSE c_main;

            if :v_output is null then
				v_output := v_out;
		    else
		    	v_output := v_output|| ', '||v_out;
		    end if;

			i = :i + 1;
		END WHILE;

		SELECT 'out: '||v_output FROM dummy;
END;
