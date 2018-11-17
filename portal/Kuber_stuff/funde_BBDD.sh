#! /bin/bash
cd ../,,
find . -iname "*.pyc" -exec rm -rfv {} \;
cd portal/migrations/
rm 00*
rm -r __pycache__

cd ../..
python3 manage.py makemigrations
python3 manage.py migrate
