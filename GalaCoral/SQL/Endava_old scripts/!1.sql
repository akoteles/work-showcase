select
  event_name,
  total_waits


from
  dba_hist_system_event
where
  event_name like UPPER ('%commit%');


SYS_C00207253
ARIT_AITY_FK
ARI_AIAR_FK1
SYS_C00207455
AOMD_AAMT_FK
AOMT_PK



select * from v$fixed_table where name like '%FUNC%';



insert into user_security_roles (system_user_id, role_code, DEFAULT_SECURITY_ROLE_IND, CNTL_PROCESS, CNTL_TIMESTAMP, CNTL_LOCKSEQ, CNTL_USER_ID)


select 2810, role_code, DEFAULT_SECURITY_ROLE_IND, CNTL_PROCESS, CNTL_TIMESTAMP, CNTL_LOCKSEQ, CNTL_USER_ID from user_security_roles where system_user_id =7058;


select * from user_security_roles where system_user_id = 2810;


select * from user_security_roles where system_user_id = 7058;

select * from system_user_details sud  where nt_user_id like '%BUC%';
 sud.system_user_id=2805


 delete from user_security_roles where system_user_id =2810;
