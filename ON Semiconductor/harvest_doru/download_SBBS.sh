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
echo " ****   Download Program - Order Backlog to TARGET_SYSTEM interface - OM extension   *** "
echo " -------------------------------------------------------------------------------- "
APPSPWD=$PLACEHOLDER_SECRET
LOGFILE=download_SBBS.`date +%m%d%Y.%H%M%S`.log
while [ "$APPSPWD" = "" -o `CHKLOGIN "oracle_user/$APPSPWD@$INSTANCE"` = "NOK" ]
do
    if [ "$APPSPWD" = "" ];then
            read -s -p "Enter APPS password: " APPSPWD
    else
        echo "Enter APPS Password: "
        APPSPWD=""
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
echo " Section 4: Executing DB Scripts ..."
echo " "
if perl $FND_TOP/bin/xdfgen.pl oracle_user/$APPSPWD XXCLIENT_ORDER_FAR_STG_TBL XXCLIENT >> $LOGFILE
then
    echo "XXCLIENT_ORDER_FAR_STG_TBL.xdf downloaded successfully !" >> $LOGFILE
	echo "XXCLIENT_ORDER_FAR_STG_TBL.xdf downloaded successfully !"
else
    echo "XXCLIENT_ORDER_FAR_STG_TBL.xdf NOT downloaded !" >> $LOGFILE
	echo "XXCLIENT_ORDER_FAR_STG_TBL.xdf NOT downloaded !"
    echo "Aborting......"
    exit 1
fi
if $FND_TOP/bin/FNDLOAD oracle_user/$APPSPWD@$INSTANCE 0 Y DOWNLOAD $FND_TOP/patch/115/import/afcpprog.lct XXCLIENT_ORDER_BACKLOG_CP.ldt PROGRAM APPLICATION_SHORT_NAME="XXCLIENT" CONCURRENT_PROGRAM_NAME="XXCLIENT_ORDER_BACKLOG"
then
    echo "XXCLIENT_ORDER_BACKLOG_CP.ldt downloaded successfully"
    echo "XXCLIENT_ORDER_BACKLOG_CP.ldt downloaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_BACKLOG_CP.ldt NOT downloaded"
    echo "XXCLIENT_ORDER_BACKLOG_CP.ldt NOT downloaded" >> $LOGFILE
    exit 1
fi
if $FND_TOP/bin/FNDLOAD oracle_user/$APPSPWD@$INSTANCE 0 Y DOWNLOAD $FND_TOP/patch/115/import/afcpprog.lct XXCLIENT_ORDER_FAR_STG_TBL_CP.ldt PROGRAM APPLICATION_SHORT_NAME="XXCLIENT" CONCURRENT_PROGRAM_NAME="XXCLIENT_ORDER_FAR_STG_TBL"
then
    echo "XXCLIENT_ORDER_FAR_STG_TBL_CP.ldt downloaded successfully"
    echo "XXCLIENT_ORDER_FAR_STG_TBL_CP.ldt downloaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_FAR_STG_TBL_CP.ldt NOT downloaded"
    echo "XXCLIENT_ORDER_FAR_STG_TBL_CP.ldt NOT downloaded" >> $LOGFILE
    exit 1
fi
if $FND_TOP/bin/FNDLOAD oracle_user/$APPSPWD@$INSTANCE 0 Y DOWNLOAD $FND_TOP/patch/115/import/aflvmlu.lct XXCLIENT_ORDER_BACKLOG_CODE_LKP.ldt FND_LOOKUP_TYPE APPLICATION_SHORT_NAME="XXCLIENT" LOOKUP_TYPE="XXCLIENT_ORDER_BACKLOG_CODE"
then
    echo "XXCLIENT_ORDER_BACKLOG_CODE_LKP.ldt downloaded successfully"
    echo "XXCLIENT_ORDER_BACKLOG_CODE_LKP.ldt downloaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_BACKLOG_CODE_LKP.ldt NOT downloaded"
    echo "XXCLIENT_ORDER_BACKLOG_CODE_LKP.ldt NOT downloaded" >> $LOGFILE
    exit 1
fi
if $FND_TOP/bin/FNDLOAD oracle_user/$APPSPWD@$INSTANCE 0 Y DOWNLOAD $FND_TOP/patch/115/import/aflvmlu.lct XXCLIENT_OM_EMAIL_NOTIFICATION_LKP.ldt FND_LOOKUP_TYPE APPLICATION_SHORT_NAME="XXCLIENT" LOOKUP_TYPE="XXCLIENT_OM_EMAIL_NOTIFICATION"
then
    echo "XXCLIENT_OM_EMAIL_NOTIFICATION_LKP.ldt downloaded successfully"
    echo "XXCLIENT_OM_EMAIL_NOTIFICATION_LKP.ldt downloaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_OM_EMAIL_NOTIFICATION_LKP.ldt NOT downloaded"
    echo "XXCLIENT_OM_EMAIL_NOTIFICATION_LKP.ldt NOT downloaded" >> $LOGFILE
    exit 1
fi
if $FND_TOP/bin/FNDLOAD oracle_user/$APPSPWD@$INSTANCE 0 Y DOWNLOAD $FND_TOP/patch/115/import/aflvmlu.lct XXCLIENT_OM_CURRENCY_CODE_LKP.ldt FND_LOOKUP_TYPE APPLICATION_SHORT_NAME="XXCLIENT" LOOKUP_TYPE="XXCLIENT_OM_CURRENCY_CODE"
then
    echo "XXCLIENT_OM_CURRENCY_CODE_LKP.ldt downloaded successfully"
    echo "XXCLIENT_OM_CURRENCY_CODE_LKP.ldt downloaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_OM_CURRENCY_CODE_LKP.ldt NOT downloaded"
    echo "XXCLIENT_OM_CURRENCY_CODE_LKP.ldt NOT downloaded" >> $LOGFILE
    exit 1
fi
if $FND_TOP/bin/FNDLOAD oracle_user/$APPSPWD@$INSTANCE 0 Y DOWNLOAD $FND_TOP/patch/115/import/afscprof.lct XXCLIENT_ORDER_BACKLOG_RUN_DATE_PRF.ldt PROFILE PROFILE_NAME="XXCLIENT_ORDER_BACKLOG_RUN_DATE" APPLICATION_SHORT_NAME="XXCLIENT"
then
    echo "XXCLIENT_ORDER_BACKLOG_RUN_DATE_PRF.ldt downloaded successfully"
    echo "XXCLIENT_ORDER_BACKLOG_RUN_DATE_PRF.ldt downloaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_BACKLOG_RUN_DATE_PRF.ldt NOT downloaded"
    echo "XXCLIENT_ORDER_BACKLOG_RUN_DATE_PRF.ldt NOT downloaded" >> $LOGFILE
    exit 1
fi
if $FND_TOP/bin/FNDLOAD oracle_user/$APPSPWD@$INSTANCE 0 Y DOWNLOAD $FND_TOP/patch/115/import/afmdmsg.lct XXCLIENT_ORDER_FAR_STG_PKG_MSG.ldt FND_NEW_MESSAGES APPLICATION_SHORT_NAME="XXCLIENT" MESSAGE_NAME="XXCLIENT_ORDER_FAR_STG_PKG%"
then
    echo "XXCLIENT_ORDER_FAR_STG_PKG_MSG.ldt downloaded successfully"
    echo "XXCLIENT_ORDER_FAR_STG_PKG_MSG.ldt downloaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_FAR_STG_PKG_MSG.ldt NOT downloaded"
    echo "XXCLIENT_ORDER_FAR_STG_PKG_MSG.ldt NOT downloaded" >> $LOGFILE
    exit 1
fi
if $FND_TOP/bin/FNDLOAD oracle_user/$APPSPWD@$INSTANCE 0 Y DOWNLOAD $FND_TOP/patch/115/import/afmdmsg.lct XXCLIENT_ORDER_BACKLOG_PK_MSG.ldt FND_NEW_MESSAGES APPLICATION_SHORT_NAME="XXCLIENT" MESSAGE_NAME="XXCLIENT_ORDER_BACKLOG_PK%"
then
    echo "XXCLIENT_ORDER_BACKLOG_PK_MSG.ldt downloaded successfully"
    echo "XXCLIENT_ORDER_BACKLOG_PK_MSG.ldt downloaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_BACKLOG_PK_MSG.ldt NOT downloaded"
    echo "XXCLIENT_ORDER_BACKLOG_PK_MSG.ldt NOT downloaded" >> $LOGFILE
    exit 1
fi
if $FND_TOP/bin/FNDLOAD oracle_user/$APPSPWD@$INSTANCE 0 Y DOWNLOAD $FND_TOP/patch/115/import/afffload.lct XXCLIENT_ORDER_FAR_FEED_REGION_CODE_VL.ldt VALUE_SET FLEX_VALUE_SET_NAME="XXCLIENT_ORDER_FAR_FEED_REGION_CODE"
then
    echo "XXCLIENT_ORDER_FAR_FEED_REGION_CODE_VL.ldt downloaded successfully"
    echo "XXCLIENT_ORDER_FAR_FEED_REGION_CODE_VL.ldt downloaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_FAR_FEED_REGION_CODE_VL.ldt NOT downloaded"
    echo "XXCLIENT_ORDER_FAR_FEED_REGION_CODE_VL.ldt NOT downloaded" >> $LOGFILE
    exit 1
fi

echo " "
echo " "
echo "Downloaded all components successfully ..."
echo "Please review "$LOGFILE
exit
