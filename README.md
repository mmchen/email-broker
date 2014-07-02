Email Service Broker
====================

On this page:

* [Introduction](https://github.com/mmchen/email-broker/overview#introduction)
* [Structure of This Application](https://github.com/mmchen/email-broker/overview#structure-of-this-application)
* [How to Run The Application](https://github.com/mmchen/email-broker/overview#how-to-run-the-application)
* [Software Dependencies](https://github.com/mmchen/email-broker/overview#software-dependencies)
* [Features](https://github.com/mmchen/email-broker/overview#features)
* [Todo Features](https://github.com/mmchen/email-broker/overview#todo-features)
* [Client Email json File Example](https://github.com/mmchen/email-broker/overview#client-email-json-file-example)
* [Contact](https://github.com/mmchen/email-broker/overview#Contact)

# Introduction

This application creates an HTTP service that provides an abstraction between two different email service providers. This way, if one of the services goes down, we quickly failover to a different provider without affecting your customers.

The HTTP service accepts POST requests with JSON data to a '/email' endpoint with the following parameters (all fields are required):

● ‘to’ ­ The email address to send to

● ‘to\_name’ ­ The name to accompany the email

● ‘from’ ­ The email address in the from and reply fields

● ‘from\_name’ ­ The name to accompany the from/reply emails

● ‘subject’ ­ The subject line of the email

● ‘body’ ­ The HTML body of the email

There are also a list optional fields:

● ‘cc’ ­ The email address to cc

● ‘bcc’ ­ The email address to bcc

● ‘delivery\_time’ ­ The scheduled delivery time (must be a UTC timestamp in YYYY-MM-DD HH:MM:SS format)

# Structure of This Application

  FILES             |  Description
 :----------------- | :---------------------------------------------------------------------
 `README.md`        |  README file used on GitHub homepage
 `emailServer.py`   |  main entry of the application
 `config.py`        |  default configuration file
 `config.json`      |  an example configuration json file

  DIRECTORIES       |  Description
 :----------------- | :---------------------------------------------------------------------
 `test/`            |  test automations which test various functionalities of the 
                    |  application, there is a README under this directory elaberates
                    |  what different test cases are and how to run the test scripts.
                    |  regress.sh is the main test script. If any changes is made to the
                    |  source code, simply run './regress.sh' to protect the code from
                    |  regression.

# How to Run The Application

The installation is easy, simply download the application.

Run:

    python emailServer.py

It will start the email service on port 5000 using the default configuration in config.py. Any change in config.py requires a re-deloyment of the service.

or run:

    python emailServer.py config.json

It will start the email service with loading config.json (could be other name) dynamically. Any change in config.json doesn't require a restart of the service without affecting the clients.

# Software Dependencies

This software is implemented in Python and uses Flask, you may run 'pip install Flask' to install Flask.

The reason of choosing Python and Flask is simple, it is easy to write Python codes and Flask is a lightweight web application framework which suits the need of this application.


# Features

This application has fulfilled the required functionality and implementation requirements:

● The service will first validate the input fields. Check if there are any missing required fields; check if there are any unsupported/duplicate fields; check if the email addresses are valid (for example, fake@example is an invalid email address).

● Convert the 'body' HTML to a plain text version. For some special HTML tags, like <p>, <br>, we replace them with the corresponding texts. Otherwise, we simply remove the HTML tags.

● The service will send email via the provider of mailgun by default, but a simple change in config.py or configuration json file will switch over to the other provider of mandrill. 

This application also implements the following additional features:

● Provide optional fields in the email, such as 'cc', 'bcc', and 'delivery\_time'.

● The field of 'delivery\_time' is used for delayed delivery. Clients may provide a UTC format date / time for delivery.

● Dynamtically select a provider based on their error responses. The application will select the default provider as configured for the first time, once the provider started to timeout or returning errors, it will automatically switch to the other.

● We can specify 'persist' parameter in config file to specify the location to persist the emails sent through to a csv file which can be loaded to DBMS such as MySQL for queries. Each record includes the provider that it is sent through, sent timestamp, and all the required and optional fields.

● We can specify 'timeout' parameter in config file to control the timeout when POST requests to a provider.

● It is possible that two providers are both down. We can specify 'retries' parameter in config file to specify the number of retries if both providers are down.

● We can specify 'logfile' parameter in config file to log DEBUG level traces to log file for debugging purpose.

# Todo features

If spending additional time, the following features may be implemented:

● Both Mandrill and Mailgun have webhooks for email opens and clicks. An endpoint could be implemented on the service to receive those webhook POST requests and store that information in some form of data storage. 

● The fields of 'to', 'from' (also 'cc' and 'bcc') only support one email address now. Simple changes could be made to split the email addresses and add them to the POST request to the provider.

# Client Email json File Example


{

    "to": "green@example.com",

    "to_name": "Ms. Green",

    "from": "noreply@example.com",

    "from_name": "Example.com",

    "subject": "A Message from example.com",

    "body": "Dear client,<br><p>This is a sample example.</p>",

    "cc": "someone@example.com",

    "delivery_time": "2014-06-15 16:43:00"

}

# Contact

If you have any question or comments, please contact Mingmin Chen at mikemmchen@gmail.com.
