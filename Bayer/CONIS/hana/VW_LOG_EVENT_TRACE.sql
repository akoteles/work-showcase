
Drop  VIEW VW_LOG_EVENT_TRACE;


Create VIEW VW_LOG_EVENT_TRACE as
select *
from (
   	select distinct
			s.pid 								as "JOB_ID",
			s1.job 								as "JOB_NAME",
			case when s.root_pid=s.father_pid then 'MAIN'
			     else s.job
			 end                                as "COMP_NAME",
			'TAC'	 							as "EVENT_SOURCE",
			case when s.message_type like '%begin%' then 'JOB_START'
			     when s.message_type like '%end%'   then 'JOB_END'
			end 	      						as "EVENT_CLASS" ,
			s.message||' '||CHAR(10)||
			'Duration: '|| s.duration||
			' seconds'	    				    as "EVENT_MESSAGE" ,
			s.moment	      					as "EVENT_TIMESTAMP",
			s.root_pid,
			s.father_pid
	  from SOURCE_SYSTEM_A_OP.TAC_STATS s
cross join ( select job from SOURCE_SYSTEM_A_OP.TAC_STATS where root_pid=father_pid ) s1
	 where (   s.pid in ( select pid from SOURCE_SYSTEM_A_OP.TAC_STATS where root_pid=father_pid )
	        or s.father_pid in ( select pid from SOURCE_SYSTEM_A_OP.TAC_STATS where root_pid=father_pid )
	       )
	 and s.message_type like '%begin%'
	order by s.moment
   )
UNION ALL
select *
from (
	select distinct
		l.pid 								as "JOB_ID",
		s.job	      						as "JOB_NAME" ,
		case when s.job=l.job then 'MAIN'
		     else l.job
		 end       			     			as "COMP_NAME",
		'TAC'	      						as "EVENT_SOURCE",
		case when l.code = 991 then 'ERROR_MAJOR_A'
		     when l.code = 992 then 'ERROR_MAJOR_B'
		     when l.code = 993 then 'ERROR_MAJOR_C'
		     when l.code = 994 then 'ERROR_MAJOR_D'
		     when l.code = 881 then 'VALIDATION_MAJOR_A'
		     when l.code = 882 then 'VALIDATION_MAJOR_B'
		     when l.code = 883 then 'VALIDATION_MINOR_A'
	         else 'ERROR_MINOR_A'
		end           						as "EVENT_CLASS" ,
		  l.message	    				    as "EVENT_MESSAGE" ,
		l.moment  	  						as "EVENT_TIMESTAMP",
		l.root_pid,
		l.father_pid
	from SOURCE_SYSTEM_A_OP.TAC_STATS s
   inner join SOURCE_SYSTEM_A_OP.TAC_LOG l on  s.pid = l.pid
   order by l.moment
  )
UNION ALL
select *
from (
	select distinct
		m.pid 								as "JOB_ID",
		s.job	      						as "JOB_NAME" ,
		case when s.job=m.job then 'MAIN'
		     else m.job
		 end       			     			as "COMP_NAME",
		'TAC'	      						as "EVENT_SOURCE",
		'ROWS_AFFECTED'  					as "EVENT_CLASS" ,
		'Context: '    || m.context ||' -> '||CHAR(10)||
	    'Origin: '     || m.origin ||' -> '||CHAR(10)||
		'Label: '      || m.label ||' -> '||CHAR(10)||
		'Count: '      || m.count ||' -> '||CHAR(10)||
		'Ref: '        || case when m.reference is null then 'NA' end
											as "EVENT_MESSAGE" ,
		m.moment  	  						as "EVENT_TIMESTAMP",
		m.root_pid,
		m.father_pid
	from SOURCE_SYSTEM_A_OP.TAC_STATS s
   inner join SOURCE_SYSTEM_A_OP.TAC_METER m on  s.pid = m.father_pid
   order by m.moment
  )
UNION ALL
select *
from (
   	select distinct
			s.pid 								as "JOB_ID",
			s1.job 								as "JOB_NAME",
			case when s.root_pid=s.father_pid then 'MAIN'
			     else s.job
			 end                                as "COMP_NAME",
			'TAC'	 							as "EVENT_SOURCE",
			case when s.message_type like '%begin%' then 'JOB_START'
			     when s.message_type like '%end%'   then 'JOB_END'
			end 	      						as "EVENT_CLASS" ,
			'Message: '||s.message||' -> '||CHAR(10)||
			'Duration: '|| s.duration||
			' seconds'	    				    as "EVENT_MESSAGE" ,
			s.moment	      					as "EVENT_TIMESTAMP",
			s.root_pid,
			s.father_pid
	  from SOURCE_SYSTEM_A_OP.TAC_STATS s
cross join ( select job from SOURCE_SYSTEM_A_OP.TAC_STATS where root_pid=father_pid ) s1
	 where (   s.pid in ( select pid from SOURCE_SYSTEM_A_OP.TAC_STATS where root_pid=father_pid )
	        or s.father_pid in ( select pid from SOURCE_SYSTEM_A_OP.TAC_STATS where root_pid=father_pid )
	       )
	 and s.message_type like '%end%'
	order by s.moment
   )
