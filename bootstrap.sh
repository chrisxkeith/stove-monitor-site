cd ~
random=`cat /dev/urandom | tr -cd 'a-f0-9' | head -c 4`
mv ~/cloudshell_open/stove-monitor-site ~/cloudshell_open/stove-monitor-site-${random}
cloudshell_open --repo_url "https://github.com/chrisxkeith/stove-monitor-site.git" --page "editor" --force_new_clone
            ; if $? -ne 0 ; then exit -666
cd ~/cloudshell_open/stove-monitor-site
            ; if $? -ne 0 ; then exit -666
gcloud config set project stove-monitor
            ; if $? -ne 0 ; then exit -666
pip3 install -r requirements.txt --user
            ; if $? -ne 0 ; then exit -666
pip3 install PyParticleIO --user
            ; if $? -ne 0 ; then exit -666
pip3 install python-dotenv
            ; if $? -ne 0 ; then exit -666
cd bookshelf
            ; if $? -ne 0 ; then exit -666
cp ~/.env .
            ; if $? -ne 0 ; then exit -666
~/.local/bin/gunicorn -b :8080 main:app
