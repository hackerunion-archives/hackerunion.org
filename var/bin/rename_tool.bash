#!/bin/bash
# Brandon Diamond -- replace words in bulk

if (( $# < 2 )); then
  echo "$0 find replace"
  exit 1
fi

for file in `grep -lr "$1" . | grep -v '.pyc' | grep -v '.svn'`; do
  echo $file
  sed -e "s/$1/$2/g" < $file > $file.tmp;
  mv $file.tmp $file;
done
