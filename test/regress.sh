#!/usr/bin/env sh

# start the server with default setting
python ../emailServer.py >& /dev/null &
mypid=$!

# wait for the server to bootstrap
sleep 5

# run different test cases and check if outputs are expected.
# The test cases include email json files with missing
# required fields, duplicate fields, optional fields, or
# not even an email json file.
./testcase.sh a default
./testcase.sh b default
./testcase.sh c default
./testcase.sh d default
./testcase.sh e default
./testcase.sh f default
./testcase.sh g default

# end the server
kill $mypid
wait $mypid >/dev/null 2>&1

# start the server with mandrill as service provider as
# specified in config1.json file.
python ../emailServer.py config1.json >& /dev/null &
mypid=$!

# wait for the server to bootstrap
sleep 5

# Run the two tests with valid email json files and
# verify that the output is expected
./testcase.sh a mandrill
./testcase.sh g mandrill

# end the server
kill $mypid
wait $mypid >/dev/null 2>&1

# start the server with mailgun as service provider
python ../emailServer.py config2.json >& /dev/null &
mypid=$!

# wait for the server to bootstrap
sleep 5

# Run the two tests with valid email json files and
# verify that the output is expected
./testcase.sh a mailgun
./testcase.sh g mailgun

# end the server
kill $mypid
wait $mypid >/dev/null 2>&1

# check if the email persistence feature works
# we have turned on the sent email persistence feature
# make sure the emails recorded in the csv
if ! [[ -f emailSent.csv ]]; then
  echo "There is no emailSent.csv!"
  echo "Test of email persistence feature FAILED!"
elif [[ -n "$(diff -I "\".*\"" emailSent.csv expected/emailSent.csv)" ]]; then
  diff -I "\".*\"" emailSent.csv expected/emailSent.csv > emailSent.dif;
  echo "There is new dif in emailSent.dif!"
  echo "Test of email persistence feature FAILED!"
else
  #rm emailSent.csv;
  echo "Test of email persistence feature SUCCESSED!"
fi

# delete the server debug log if all tests succeeded
ls *.dif >& /dev/null
if [[ $? -eq 0 ]]; then
  echo "WARNING: please look at the *.dif file(s)!"
else
  rm emailServer.log
fi
