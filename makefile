sudo apt-get install nginx

virtualenv env
./env/bin/pip install -r requirements.txt

sudo ln -s /home/leebird/Projects/django-annotation/config/django_annotation_nginx.conf /etc/nginx/sites-enabled/
mkdir log
mkdir socket

./env/bin/python manage.py collectstatic