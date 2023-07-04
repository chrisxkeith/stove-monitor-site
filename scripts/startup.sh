# . cloudshell_open/stove-monitor-site/scripts/startup.sh
gcloud config set project stove-monitor                     ; if [ $? -ne 0 ] ; then exit -6 ; fi
cd ~/cloudshell_open/stove-monitor-site/bookshelf           ; if [ $? -ne 0 ] ; then exit -6 ; fi
