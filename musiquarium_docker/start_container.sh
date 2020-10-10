docker run -d \
    -p 8006:8000 \
    -e "SECRET_KEY=foo" -e "DEBUG=1" -e "DJANGO_ALLOWED_HOSTS=*" \
    robstrong/musiquarium:testing python /usr/src/app/manage.py runserver 0.0.0.0:8000
