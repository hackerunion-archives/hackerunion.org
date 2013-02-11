#!/bin/bash

if [ ! -f ../manage.py -o ! -f petri.db ]; then
  echo "Invalid usage. Manage.py must be in parent directory and database must be in current directory."
  exit 1
fi

export DJANGO_LOCAL=True 
export DJANGO_DEBUG=True

if [[ "$#" == 1 && "$1" == "sync" ]]; then
  rm petri.db && python ../manage.py syncdb
else
  yes yes | python ../manage.py collectstatic | python ../manage.py runserver
fi
