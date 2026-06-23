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
echo " -------------------------------------------------------------------- "
echo " ****   Download Program - FEED_SYSTEM to TARGET_SYSTEM interface - OM extension   *** "
echo " -------------------------------------------------------------------- "
APPSPWD=$PLACEHOLDER_SECRET
LOGFILE=download_SFEED.`date +%m%d%Y.%H%M%S`.log
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
if perl $FND_TOP/bin/xdfgen.pl oracle_user/$APPSPWD XXCLIENT_ORDER_FEED_STG XXCLIENT >> $LOGFILE
then
    echo "XXCLIENT_ORDER_FEED_STG.xdf downloaded successfully !" >> $LOGFILE
	echo "XXCLIENT_ORDER_FEED_STG.xdf downloaded successfully !"
else
    echo "XXCLIENT_ORDER_FEED_STG.xdf NOT downloaded !" >> $LOGFILE
	echo "XXCLIENT_ORDER_FEED_STG.xdf NOT downloaded !"
    echo "Aborting......"
    exit 1
fi
if perl $FND_TOP/bin/xdfgen.pl oracle_user/$APPSPWD XXCLIENT_ORDER_TARGET_STG XXCLIENT >> $LOGFILE
then
    echo "XXCLIENT_ORDER_TARGET_STG.xdf downloaded successfully !" >> $LOGFILE
	echo "XXCLIENT_ORDER_TARGET_STG.xdf downloaded successfully !"
else
    echo "XXCLIENT_ORDER_TARGET_STG.xdf NOT downloaded !" >> $LOGFILE
	echo "XXCLIENT_ORDER_TARGET_STG.xdf NOT downloaded !"
    echo "Aborting......"
    exit 1
fi
if perl $FND_TOP/bin/xdfgen.pl oracle_user/$APPSPWD XXCLIENT_ORDER_FEED_DATE_COMPARE XXCLIENT >> $LOGFILE
then
    echo "XXCLIENT_ORDER_FEED_DATE_COMPARE.xdf downloaded successfully !" >> $LOGFILE
	echo "XXCLIENT_ORDER_FEED_DATE_COMPARE.xdf downloaded successfully !"
else
    echo "XXCLIENT_ORDER_FEED_DATE_COMPARE.xdf NOT downloaded !" >> $LOGFILE
	echo "XXCLIENT_ORDER_FEED_DATE_COMPARE.xdf NOT downloaded !"
    echo "Aborting......"
    exit 1
fi
if perl $FND_TOP/bin/xdfgen.pl oracle_user/$APPSPWD XXCLIENT_ORDER_FEED_COMPARE XXCLIENT >> $LOGFILE
then
    echo "XXCLIENT_ORDER_FEED_COMPARE.xdf downloaded successfully !" >> $LOGFILE
	echo "XXCLIENT_ORDER_FEED_COMPARE.xdf downloaded successfully !"
else
    echo "XXCLIENT_ORDER_FEED_COMPARE.xdf NOT downloaded !" >> $LOGFILE
	echo "XXCLIENT_ORDER_FEED_COMPARE.xdf NOT downloaded !"
    echo "Aborting......"
    exit 1
fi
if perl $FND_TOP/bin/xdfgen.pl oracle_user/$APPSPWD XXCLIENT_ORDER_FEED_REGION_BATCH_CODES XXCLIENT >> $LOGFILE
then
    echo "XXCLIENT_ORDER_FEED_REGION_BATCH_CODES.xdf downloaded successfully !" >> $LOGFILE
	echo "XXCLIENT_ORDER_FEED_REGION_BATCH_CODES.xdf downloaded successfully !"
else
    echo "XXCLIENT_ORDER_FEED_REGION_BATCH_CODES.xdf NOT downloaded !" >> $LOGFILE
	echo "XXCLIENT_ORDER_FEED_REGION_BATCH_CODES.xdf NOT downloaded !"
    echo "Aborting......"
    exit 1
fi
if perl $FND_TOP/bin/xdfgen.pl oracle_user/$APPSPWD CLIENT_EBS_CONTROL XXCLIENT >> $LOGFILE
then
    echo "CLIENT_EBS_CONTROL.xdf downloaded successfully !" >> $LOGFILE
	echo "CLIENT_EBS_CONTROL.xdf downloaded successfully !"
else
    echo "CLIENT_EBS_CONTROL.xdf NOT downloaded !" >> $LOGFILE
	echo "CLIENT_EBS_CONTROL.xdf NOT downloaded !"
    echo "Aborting......"
    exit 1
fi
if $FND_TOP/bin/FNDLOAD oracle_user/$APPSPWD@$INSTANCE 0 Y DOWNLOAD $FND_TOP/patch/115/import/aflvmlu.lct XXCLIENT_ORDER_FEED_REGION_BATCH_CODES_LKP.ldt FND_LOOKUP_TYPE APPLICATION_SHORT_NAME="APPS" LOOKUP_TYPE="XXCLIENT_ORDER_FEED_REGION_BATCH_CODES"
then
    echo "XXCLIENT_ORDER_FEED_REGION_BATCH_CODES_LKP.ldt downloaded successfully"
    echo "XXCLIENT_ORDER_FEED_REGION_BATCH_CODES_LKP.ldt downloaded successfully" >> $LOGFILE
else
    echo "XXCLIENT_ORDER_FEED_REGION_BATCH_CODES_LKP.ldt NOT downloaded"
    echo "XXCLIENT_ORDER_FEED_REGION_BATCH_CODES_LKP.ldt NOT downloaded" >> $LOGFILE
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

echo " "
echo " "
echo "Downloaded all components successfully ..."
echo "Please review "$LOGFILE
exit
