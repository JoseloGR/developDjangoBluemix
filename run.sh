if [ -z "$VCAP_APP_PORT"];
  then SERVER_PORT=8000;
else SERVER_PORT="$VCAP_APP_PORT";
fi

echo [$0] port is----------- $SERVER_PORT
python manage.py makemigrations
python manage.py migrate
python manage.py syncdb --noinput
#python manage.py collectstatic --noinput

python manage.py runserver 0.0.0.0:$SERVER_PORT --noreload
