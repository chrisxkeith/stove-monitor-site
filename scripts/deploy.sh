cd ~/cloudshell_open/stove-monitor-site/bookshelf                          ; if [ $? -ne 0 ] ; then exit -6 ; fi
time gcloud builds submit --tag gcr.io/stove-monitor/bookshelf .           ; if [ $? -ne 0 ] ; then exit -6 ; fi
time gcloud run deploy bookshelf --image gcr.io/stove-monitor/bookshelf --platform managed --region us-central1 --allow-unauthenticated
                                                                             if [ $? -ne 0 ] ; then exit -6 ; fi
