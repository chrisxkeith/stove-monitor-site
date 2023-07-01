cd ~
random=`cat /dev/urandom | tr -cd 'a-f0-9' | head -c 4`             ; if [ $? -ne 0 ] ; then exit -6 ; fi
mv ~/cloudshell_open/stove-monitor-site ~/cloudshell_open/stove-monitor-site-${random}
cloudshell_open --repo_url "https://github.com/chrisxkeith/stove-monitor-site.git" --page "editor" --force_new_clone
                                                                      if [ $? -ne 0 ] ; then exit -6 ; fi
cd ~/cloudshell_open/stove-monitor-site                             ; if [ $? -ne 0 ] ; then exit -6 ; fi
gcloud config set project stove-monitor                             ; if [ $? -ne 0 ] ; then exit -6 ; fi
pip3 install -r requirements.txt --user                             ; if [ $? -ne 0 ] ; then exit -6 ; fi
cd bookshelf                                                        ; if [ $? -ne 0 ] ; then exit -6 ; fi
cp ~/.env .                                                         ; if [ $? -ne 0 ] ; then exit -6 ; fi
~/.local/bin/gunicorn -b :8080 main:app
