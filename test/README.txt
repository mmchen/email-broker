##################################################################
                 Test Automation README
##################################################################

This folder contains regression test scripts and different test
cases to test different features of this applications.

# How to Run Tests

Simply run:

    ./regress.sh

It will list the testcases which succeeded and which failed.

# Test Files
Test scripts:

 - regress.sh:   the entry point of running the whole suite of
                 the test cases
 - testcase.sh:  post a post request to the service and check
                 whether the output is expected or not

Config files:

 - config1.json  set 'mandrill' as the default 'provider'
 - config2.json  without setting 'provider'

Test cases (under cases/):

 - a.json:       an email json file with all the required fields
 - b.json:       not even a json file
 - c.json:       an email json file with missing required fields
 - d.json:       an email json file with duplicate fields
 - e.json:       an email json file with unsupported fields
 - f.json:       an email json file with invalid email addresses
 - g.json:       an email json file with delivery time

Expected results (under expected/)
