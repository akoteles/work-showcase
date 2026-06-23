#! /bin/sh
CHKLOGIN(){
    if sqlplus -s /nolog <<! >/dev/null 2>&1
          WHENEVER SQLERROR EXIT 1;
          CONNECT $1 ;

          EXIT;
!
    then
        echo OK
    else
        echo NOK
    fi
}
echo " -------------------------------------------------------------------------------- "
echo " ****   UPLOAD Program - OM_INT_FEED_To_ORACLE TARGET_SYSTEM DAILY FEED BY REGION   *** "
echo " -------------------------------------------------------------------------------- "
echo " The installer expects:                                                           "
echo "     SQL  files  - to be placed in \$CLIENT_TOP/sql                                "
echo "     CTL  files  - to be placed in \$CLIENT_TOP/bin                                "
echo "     SH   files  - to be placed in \$CLIENT_TOP/bin                                "
echo "     LDT  files  - to be placed in \$CLIENT_TOP/admin                              "
echo "     WFT  files  - to be places in \$CLIENT_TOP/admin                              "
echo "     FMB  Files  - to be placed in \$CLIENT_TOP/forms/US                           "
echo "     RDF  Files  - to be placed in \$CLIENT_TOP/reports/US                         "
echo "     RTF  Files  - to be placed in \$CLIENT_TOP/reports/US                         "
echo " -------------------------------------------------------------------------------- "
ORACLE_USER_PWD=$PLACEHOLDER_SECRET
CLIENT_USER_PWD=$PLACEHOLDER_SECRET
INSTANCE=$TWO_TASK
LOGFILE=$APPLCSF/$HARVESTLOG/OM_FEED_TO_ORACLE_TARGET_DAILY_FEED.`date +%m%d%Y.%H%M%S`.log
while [ "$INSTANCE" = "" ]
do
    if [ "$INSTANCE" = "" ];then
            echo "Enter Instance Name: "
            read INSTANCE
    else
        echo "Enter Instance Name: "
        INSTANCE=""
    fi
done

echo " "
while [ "$ORACLE_USER_PWD" = "" -o `CHKLOGIN "oracle_user/$ORACLE_USER_PWD@$INSTANCE"` = "NOK" ]
do
    if [ "$ORACLE_USER_PWD" = "" ];then
            read -s -p "Enter APPS password: " ORACLE_USER_PWD
    else
        echo "Enter APPS Password: "
        ORACLE_USER_PWD=""
    fi
done

echo " "
while [ "$CLIENT_USER_PWD" = "" -o `CHKLOGIN "oracle_user/$CLIENT_USER_PWD@$INSTANCE"` = "NOK" ]
do
    if [ "$CLIENT_USER_PWD" = "" ];then
            read -s -p "Enter schema password: " CLIENT_USER_PWD
    else
        echo "Enter schema Password: "
        CLIENT_USER_PWD=""
    fi
done

echo " "
handle_error()
{
    if [ $? = 0 ]
    then
        echo "Copied file $1"
    else
        echo "Failed to copy the file $1. For further details please check the log file: "
        exit 2
    fi
}
echo " Section 1: Copying code files to applicable destinations ..."

cp -f ./xxclient_order_far_stg_tbl.xdf $CLIENT_TOP/patch/115/xdf/
cp -f ./XXCLIENT_ORDER_FAR_STG_TBL_grants.sql $CLIENT_TOP/sql
cp -f ./XXCLIENT_ORDER_BACKLOG_RUN_DATE_PRF.ldt $CLIENT_TOP/admin
cp -f ./XXCLIENT_ORDER_FAR_STG_PKG_MSG.ldt $CLIENT_TOP/admin
cp -f ./XXCLIENT_ORDER_BACKLOG_PK_MSG.ldt $CLIENT_TOP/admin
cp -f ./XXCLIENT_ORDER_FAR_FEED_REGION_CODE_VL.ldt $CLIENT_TOP/admin
cp -f ./XXCLIENT_ORDER_BACKLOG_CODE_LKP.ldt $CLIENT_TOP/admin
cp -f ./XXCLIENT_ORDER_FAR_STG_PKG.pks $CLIENT_TOP/sql
cp -f ./XXCLIENT_ORDER_FAR_STG_PKG.pkb $CLIENT_TOP/sql
cp -f ./XXCLIENT_ORDER_BACKLOG_PKG.pks $CLIENT_TOP/sql
cp -f ./XXCLIENT_ORDER_BACKLOG_PKG.pkb $CLIENT_TOP/sql
cp -f ./XXCLIENT_ORDER_BACKLOG_CP.ldt $CLIENT_TOP/admin
cp -f ./XXCLIENT_ORDER_FAR_STG_TBL_CP.ldt $CLIENT_TOP/admin

echo "Code files copied to destination ..."
echo " "
echo " Section 2: Converting text based files to unix format ..."

dos2unix $CLIENT_TOP/sql/XXCLIENT_ORDER_FAR_STG_TBL_grants.sql
dos2unix $CLIENT_TOP/admin/XXCLIENT_ORDER_BACKLOG_RUN_DATE_PRF.ldt
dos2unix $CLIENT_TOP/admin/XXCLIENT_ORDER_FAR_STG_PKG_MSG.ldt
dos2unix $CLIENT_TOP/admin/XXCLIENT_ORDER_BACKLOG_PK_MSG.ldt
dos2unix $CLIENT_TOP/admin/XXCLIENT_ORDER_FAR_FEED_REGION_CODE_VL.ldt
dos2unix $CLIENT_TOP/admin/XXCLIENT_ORDER_BACKLOG_CODE_LKP.ldt
dos2unix $CLIENT_TOP/sql/XXCLIENT_ORDER_FAR_STG_PKG.pks
dos2unix $CLIENT_TOP/sql/XXCLIENT_ORDER_FAR_STG_PKG.pkb
dos2unix $CLIENT_TOP/sql/XXCLIENT_ORDER_BACKLOG_PKG.pks
dos2unix $CLIENT_TOP/sql/XXCLIENT_ORDER_BACKLOG_PKG.pks
dos2unix $CLIENT_TOP/admin/XXCLIENT_ORDER_BACKLOG_CP.ldt
dos2unix $CLIENT_TOP/admin/XXCLIENT_ORDER_FAR_STG_TBL_CP.ldt

echo "ASCII files converted to UNIX format ..."
echo " "
echo " Section 3: Setting file permissions ..."

chmod 755 $CLIENT_TOP/sql/XXCLIENT_ORDER_FAR_STG_TBL_grants.sql
chmod 755 $CLIENT_TOP/admin/XXCLIENT_ORDER_BACKLOG_RUN_DATE_PRF.ldt
chmod 755 $CLIENT_TOP/admin/XXCLIENT_ORDER_FAR_STG_PKG_MSG.ldt
chmod 755 $CLIENT_TOP/admin/XXCLIENT_ORDER_BACKLOG_PK_MSG.ldt
chmod 755 $CLIENT_TOP/admin/XXCLIENT_ORDER_FAR_FEED_REGION_CODE_VL.ldt
chmod 755 $CLIENT_TOP/admin/XXCLIENT_ORDER_BACKLOG_CODE_LKP.ldt
chmod 755 $CLIENT_TOP/sql/XXCLIENT_ORDER_FAR_STG_PKG.pks
chmod 755 $CLIENT_TOP/sql/XXCLIENT_ORDER_FAR_STG_PKG.pkb
chmod 755 $CLIENT_TOP/sql/XXCLIENT_ORDER_BACKLOG_PKG.pks
chmod 755 $CLIENT_TOP/sql/XXCLIENT_ORDER_BACKLOG_PKG.pks
chmod 755 $CLIENT_TOP/admin/XXCLIENT_ORDER_BACKLOG_CP.ldt
chmod 755 $CLIENT_TOP/admin/XXCLIENT_ORDER_FAR_STG_TBL_CP.ldt

echo "Files Permission set for all files ..."
echo " "
cd $APPLCSF/$HARVESTLOG
echo "Directory changed to APPLCSF/HARVESTLOG"

echo " Section 4: Executing DB Scripts ..."
echo " "

if perl $FND_TOP/bin/xdfcmp.pl oracle_user/$CLIENT_USER_PWD@$INSTANCE $CLIENT_TOP/patch/115/xdf/xxclient_order_far_stg_tbl.xdf oracle_user/$ORACLE_USER_PWD standalone=y >> $LOGFILE
then
    echo "xxclient_order_far_stg_tbl.xdf uploaded successfully !" >> $LOGFILE
	echo "xxclient_order_far_stg_tbl.xdf uploaded successfully !"
else
    echo "xxclient_order_far_stg_tbl.xdf NOT uploaded !" >> $LOGFILE
	echo "xxclient_order_far_stg_tbl.xdf NOT uploaded !"
    echo "Aborting......"
    exit 1
fi

if sqlplus -s oracle_user/$ORACLE_USER_PWD@$INSTANCE @$CLIENT_TOP/sql/XXCLIENT_ORDER_FAR_STG_TBL_grants.sql >>$LOGFILE
then
    echo "XXCLIENT_ORDER_FAR_STG_TBL_grants.sql installed successful !" >>$LOGFILE
    echo "XXCLIENT_ORDER_FAR_STG_TBL_grants.sql installed successful !"
else
    echo "XXCLIENT_ORDER_FAR_STG_TBL_grants.sql NOT installed !" >>$LOGFILE
    echo "XXCLIENT_ORDER_FAR_STG_TBL_grants.sql NOT installed !"
    echo "Aborting......"
    exit 1
fi

if $FND_TOP/bin/FNDLOAD oracle_user/$ORACLE_USER_PWD@$INSTANCE 0 Y UPLOAD $FND_TOP/patch/115/import/afscprof.lct $CLIENT_TOP/admin/XXCLIENT_ORDER_BACKLOG_RUN_DATE_PRF.ldt - WARNING=YES UPLOAD_MODE=REPLACE CUSTOM_MODE=FORCE >>$LOGFILE
then
    echo "XXCLIENT_ORDER_BACKLOG_RUN_DATE_PRF.ldt uploaded successfully"
    echo "XXCLIENT_ORDER_BACKLOG_RUN_DATE_PRF.ldt uploaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_BACKLOG_RUN_DATE_PRF.ldt NOT uploaded"
    echo "XXCLIENT_ORDER_BACKLOG_RUN_DATE_PRF.ldt NOT uploaded" >> $LOGFILE
    exit 1
fi

if $FND_TOP/bin/FNDLOAD oracle_user/$ORACLE_USER_PWD@$INSTANCE 0 Y UPLOAD $FND_TOP/patch/115/import/afmdmsg.lct $CLIENT_TOP/admin/XXCLIENT_ORDER_FAR_STG_PKG_MSG.ldt UPLOAD_MODE=REPLACE CUSTOM_MODE=FORCE >>$LOGFILE
then
    echo "XXCLIENT_ORDER_FAR_STG_PKG_MSG.ldt uploaded successfully"
    echo "XXCLIENT_ORDER_FAR_STG_PKG_MSG.ldt uploaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_FAR_STG_PKG_MSG.ldt NOT uploaded"
    echo "XXCLIENT_ORDER_FAR_STG_PKG_MSG.ldt NOT uploaded" >> $LOGFILE
    exit 1
fi

if $FND_TOP/bin/FNDLOAD oracle_user/$ORACLE_USER_PWD@$INSTANCE 0 Y UPLOAD $FND_TOP/patch/115/import/afmdmsg.lct $CLIENT_TOP/admin/XXCLIENT_ORDER_BACKLOG_PK_MSG.ldt UPLOAD_MODE=REPLACE CUSTOM_MODE=FORCE  >>$LOGFILE
then
    echo "XXCLIENT_ORDER_BACKLOG_PK_MSG.ldt uploaded successfully"
    echo "XXCLIENT_ORDER_BACKLOG_PK_MSG.ldt uploaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_BACKLOG_PK_MSG.ldt NOT uploaded"
    echo "XXCLIENT_ORDER_BACKLOG_PK_MSG.ldt NOT uploaded" >> $LOGFILE
    exit 1
fi

if $FND_TOP/bin/FNDLOAD oracle_user/$ORACLE_USER_PWD@$INSTANCE 0 Y UPLOAD $FND_TOP/patch/115/import/afffload.lct $CLIENT_TOP/admin/XXCLIENT_ORDER_FAR_FEED_REGION_CODE_VL.ldt - WARNING=YES UPLOAD_MODE=REPLACE CUSTOM_MODE=FORCE >>$LOGFILE
then
    echo "XXCLIENT_ORDER_FAR_FEED_REGION_CODE_VL.ldt uploaded successfully"
    echo "XXCLIENT_ORDER_FAR_FEED_REGION_CODE_VL.ldt uploaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_FAR_FEED_REGION_CODE_VL.ldt NOT uploaded"
    echo "XXCLIENT_ORDER_FAR_FEED_REGION_CODE_VL.ldt NOT uploaded" >> $LOGFILE
    exit 1
fi

if $FND_TOP/bin/FNDLOAD oracle_user/$ORACLE_USER_PWD@$INSTANCE 0 Y UPLOAD $FND_TOP/patch/115/import/aflvmlu.lct $CLIENT_TOP/admin/XXCLIENT_ORDER_BACKLOG_CODE_LKP.ldt - WARNING=YES UPLOAD_MODE=REPLACE CUSTOM_MODE=FORCE >>$LOGFILE
then
    echo "XXCLIENT_ORDER_BACKLOG_CODE_LKP.ldt uploaded successfully"
    echo "XXCLIENT_ORDER_BACKLOG_CODE_LKP.ldt uploaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_BACKLOG_CODE_LKP.ldt NOT uploaded"
    echo "XXCLIENT_ORDER_BACKLOG_CODE_LKP.ldt NOT uploaded" >> $LOGFILE
    exit 1
fi

if sqlplus -s oracle_user/$ORACLE_USER_PWD@$INSTANCE @$CLIENT_TOP/sql/XXCLIENT_ORDER_FAR_STG_PKG.pks >>$LOGFILE
then
    echo "XXCLIENT_ORDER_FAR_STG_PKG.pks installed successful !" >>$LOGFILE
    echo "XXCLIENT_ORDER_FAR_STG_PKG.pks installed successful !"
else
    echo "XXCLIENT_ORDER_FAR_STG_PKG.pks NOT installed !" >>$LOGFILE
    echo "XXCLIENT_ORDER_FAR_STG_PKG.pks NOT installed !"
    echo "Aborting......"
    exit 1
fi

if sqlplus -s oracle_user/$ORACLE_USER_PWD@$INSTANCE @$CLIENT_TOP/sql/XXCLIENT_ORDER_FAR_STG_PKG.pkb >>$LOGFILE
then
    echo "XXCLIENT_ORDER_FAR_STG_PKG.pkb installed successful !" >>$LOGFILE
    echo "XXCLIENT_ORDER_FAR_STG_PKG.pkb installed successful !"
else
    echo "XXCLIENT_ORDER_FAR_STG_PKG.pkb NOT installed !" >>$LOGFILE
    echo "XXCLIENT_ORDER_FAR_STG_PKG.pkb NOT installed !"
    echo "Aborting......"
    exit 1
fi

if sqlplus -s oracle_user/$ORACLE_USER_PWD@$INSTANCE @$CLIENT_TOP/sql/XXCLIENT_ORDER_BACKLOG_PKG.pks >>$LOGFILE
then
    echo "XXCLIENT_ORDER_BACKLOG_PKG.pks installed successful !" >>$LOGFILE
    echo "XXCLIENT_ORDER_BACKLOG_PKG.pks installed successful !"
else
    echo "XXCLIENT_ORDER_BACKLOG_PKG.pks NOT installed !" >>$LOGFILE
    echo "XXCLIENT_ORDER_BACKLOG_PKG.pks NOT installed !"
    echo "Aborting......"
    exit 1
fi

if sqlplus -s oracle_user/$ORACLE_USER_PWD@$INSTANCE @$CLIENT_TOP/sql/XXCLIENT_ORDER_BACKLOG_PKG.pkb >>$LOGFILE
then
    echo "XXCLIENT_ORDER_BACKLOG_PKG.pkb installed successful !" >>$LOGFILE
    echo "XXCLIENT_ORDER_BACKLOG_PKG.pkb installed successful !"
else
    echo "XXCLIENT_ORDER_BACKLOG_PKG.pkb NOT installed !" >>$LOGFILE
    echo "XXCLIENT_ORDER_BACKLOG_PKG.pkb NOT installed !"
    echo "Aborting......"
    exit 1
fi

if $FND_TOP/bin/FNDLOAD oracle_user/$ORACLE_USER_PWD@$INSTANCE 0 Y UPLOAD $FND_TOP/patch/115/import/afcpprog.lct $CLIENT_TOP/admin/XXCLIENT_ORDER_BACKLOG_CP.ldt - WARNING=YES UPLOAD_MODE=REPLACE CUSTOM_MODE=FORCE >>$LOGFILE
then
    echo "XXCLIENT_ORDER_BACKLOG_CP.ldt uploaded successfully"
    echo "XXCLIENT_ORDER_BACKLOG_CP.ldt uploaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_BACKLOG_CP.ldt NOT uploaded"
    echo "XXCLIENT_ORDER_BACKLOG_CP.ldt NOT uploaded" >> $LOGFILE
    exit 1
fi

if $FND_TOP/bin/FNDLOAD oracle_user/$ORACLE_USER_PWD@$INSTANCE 0 Y UPLOAD $FND_TOP/patch/115/import/afcpprog.lct $CLIENT_TOP/admin/XXCLIENT_ORDER_FAR_STG_TBL_CP.ldt - WARNING=YES UPLOAD_MODE=REPLACE CUSTOM_MODE=FORCE >>$LOGFILE
then
    echo "XXCLIENT_ORDER_FAR_STG_TBL_CP.ldt uploaded successfully"
    echo "XXCLIENT_ORDER_FAR_STG_TBL_CP.ldt uploaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_FAR_STG_TBL_CP.ldt NOT uploaded"
    echo "XXCLIENT_ORDER_FAR_STG_TBL_CP.ldt NOT uploaded" >> $LOGFILE
    exit 1
fi

echo " "
echo " "
echo "Uploaded all components successfully ..."
echo "Please review "$LOGFILE
exit
