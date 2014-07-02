#!/usr/bin/env sh

curl -H "Content-Type: application/json" --data @cases/$1.json http://127.0.0.1:5000/email > $1_$2.log 2> /dev/null
if [[ -n "$(diff $1_$2.log expected/$1_$2.log)" ]]; then
  diff $1_$2.log expected/$1_$2.log > $1_$2.dif;
  echo "There is new dif in $1_$2.dif!"
  echo "Test with $1.json via $2 FAILED!"
else
  rm $1_$2.log;
  echo "Test with $1.json via $2 SUCCEEDED!"
fi
