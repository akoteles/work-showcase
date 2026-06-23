
select distinct s.* from SOURCE_SYSTEM_A_OP.TAC_STATS s
left outer join SOURCE_SYSTEM_A_OP.TAC_LOG l on  s.pid = l.father_pid
inner join SOURCE_SYSTEM_A_OP.TAC_METER m on  s.pid = m.father_pid



TRUNCATE TABLE SOURCE_SYSTEM_A_OP.TAC_STATS;
TRUNCATE TABLE SOURCE_SYSTEM_A_OP.TAC_LOG ;
TRUNCATE TABLE SOURCE_SYSTEM_A_OP.TAC_METER;

truncate table "SOURCE_SYSTEM_A_OP"."LOG_EVENT_TRACE" ;



	select * from SOURCE_SYSTEM_A_OP.VW_LOG_EVENT_TRACE v
	where v.father_pid = 'PLACEHOLDER_PID'
	order by v.EVENT_TIMESTAMP




select * from "SOURCE_SYSTEM_A_OP"."LOG_EVENT_TRACE" order by event_timestamp desc ;



	select Distinct
	       case when event_class like '%ERROR%FATAL%' then 'ABORT'
	            when event_class like '%ERROR%MINOR%' then 'RETRY'
	            else 'SUCCESS'
	        end VALIDATION_MSG,
	        event_class
	  from SOURCE_SYSTEM_A_OP.VW_LOG_EVENT_TRACE v
	where event_class not like '%JOB%' and event_class not like '%ROWS_AFFECTED%'
	  and v.root_pid = 'PLACEHOLDER_PID'


select * from SOURCE_SYSTEM_A_OP.TAC_STATS s order by s.moment

select s.* from SOURCE_SYSTEM_A_OP.TAC_LOG  s
where s.ROOT_PID='PLACEHOLDER_PID'


select s.* from SOURCE_SYSTEM_A_OP.TAC_METER  s
where s.father_pid='PLACEHOLDER_PID'

select
     to_bigint(to_char(current_date,'YYYYMMDD') || source_system_a_op.SEQ_LOG_EVENT_TRACE.nextval) as LOG_ID,
	 JOB_ID 		,
	 JOB_NAME 		,
	 COMP_NAME 		,
	 EVENT_SOURCE 	,
	 EVENT_CLASS 	,
	 EVENT_MESSAGE	,
	 EVENT_TIMESTAMP
from (
	select * from SOURCE_SYSTEM_A_OP.VW_LOG_EVENT_TRACE v
	where v.father_pid = 'PLACEHOLDER_PID'
	order by v.EVENT_TIMESTAMP
	) ;




select * from "SOURCE_SYSTEM_A_OP"."VW_LOG_EVENT_TRACE" order by event_timestamp ;


select * from "SOURCE_SYSTEM_A_OP"."VW_LOG_EVENT_TRACE" where root_pid = 'PLACEHOLDER_PID' order by event_timestamp desc;


select * from "SOURCE_SYSTEM_A_OP"."LOG_EVENT_TRACE" order by event_timestamp ;


Insert into "SOURCE_SYSTEM_A_OP"."LOG_EVENT_TRACE"
(
	 "JOB_ID" 			,
	 "JOB_NAME" 		,
	 "COMP_NAME" 		,
	 "EVENT_SOURCE" 	,
	 "EVENT_CLASS" 		,
	 "EVENT_MESSAGE"	,
	 "EVENT_TIMESTAMP"
)
select
	 v.JOB_ID 			,
	 v.JOB_NAME 		,
	 v.COMP_NAME 		,
	 v.EVENT_SOURCE 	,
	 v.EVENT_CLASS 		,
	 v.EVENT_MESSAGE	,
	 v.EVENT_TIMESTAMP
from SOURCE_SYSTEM_A_OP.VW_LOG_EVENT_TRACE v

commit;
