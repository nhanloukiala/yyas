pip install -r ./requirements.txt

python manage.py sqlclear yyasweb | ./manage.py dbshell
python manage.py syncdb

echo "from yyasweb.generateData import * ; generateRandomData();" | ./manage.py shell

python manage.py runserver