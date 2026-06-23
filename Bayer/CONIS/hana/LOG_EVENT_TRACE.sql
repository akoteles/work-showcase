
select * from SOURCE_SYSTEM_A_OP.TAC_LOG where PID='PLACEHOLDER_PID'
select source_system_a_op.SEQ_LOG_EVENT_TRACE.nextval from dummy;



drop table SOURCE_SYSTEM_A_OP.TAC_STATS ;
drop table SOURCE_SYSTEM_A_OP.TAC_LOG ;
drop table SOURCE_SYSTEM_A_OP.TAC_METER ;


drop table SOURCE_SYSTEM_A_OP.LOG_EVENT_TRACE ;

CREATE COLUMN TABLE "SOURCE_SYSTEM_A_OP"."LOG_EVENT_TRACE"
(
	 "LOG_ID" BIGINT,
	 "JOB_ID" NVARCHAR(255),
	 "JOB_NAME" NVARCHAR(255),
	 "COMP_NAME" NVARCHAR(255),
	 "EVENT_SOURCE" NVARCHAR(255),
	 "EVENT_CLASS" NVARCHAR(255),
	 "EVENT_MESSAGE" NVARCHAR(5000),
	 "EVENT_TIMESTAMP" NVARCHAR(255),
	 PRIMARY KEY ("LOG_ID")
) UNLOAD PRIORITY 5 AUTO MERGE;

drop sequence "SOURCE_SYSTEM_A_OP"."SEQ_LOG_EVENT_TRACE";

create sequence "SOURCE_SYSTEM_A_OP"."SEQ_LOG_EVENT_TRACE" increment by 1 start with 1 no cycle;




CREATE COLUMN TABLE "SOURCE_SYSTEM_A_OP"."TAC_STATS"
(
moment   timestamp,
pid      NVARCHAR(20),
father_pid  NVARCHAR(20),
root_pid     NVARCHAR(20),
system_pid   integer,
project  NVARCHAR(50),
job  NVARCHAR(255),
job_repository_id NVARCHAR(255),
job_version  NVARCHAR(255),
context   NVARCHAR(50),
origin    NVARCHAR(255),
message_type   NVARCHAR(255),
message     NVARCHAR(255),
duration  integer
) UNLOAD PRIORITY 5 AUTO MERGE;



CREATE COLUMN TABLE "SOURCE_SYSTEM_A_OP"."TAC_METER"
(
moment   timestamp,
pid      NVARCHAR(20),
father_pid  NVARCHAR(20),
root_pid     NVARCHAR(20),
system_pid   integer,
project  NVARCHAR(50),
job  NVARCHAR(255),
job_repository_id NVARCHAR(255),
job_version  NVARCHAR(255),
context   NVARCHAR(50),
origin    NVARCHAR(255),
label 	  NVARCHAR(255),
count     integer,
reference  integer,
thresholds NVARCHAR(255)
) UNLOAD PRIORITY 5 AUTO MERGE;




CREATE COLUMN TABLE "SOURCE_SYSTEM_A_OP"."TAC_LOG"
(
moment	 timestamp,
pid      NVARCHAR(20),
root_pid     NVARCHAR(20),
father_pid  NVARCHAR(20),
project  NVARCHAR(50),
job  NVARCHAR(255),
context NVARCHAR(50),
priority integer,
type NVARCHAR(255),
origin NVARCHAR(255),
message   NVARCHAR(255),
code  integer
) UNLOAD PRIORITY 5 AUTO MERGE;
