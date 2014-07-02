import sys
import json
import csv
import os.path
import requests
from re import compile
from flask import Flask, views, request
from email.utils import formatdate
from time import strptime, strftime, gmtime
from calendar import timegm
from config import *

class Email(views.MethodView):
    def __init__(self):
        # provider list, may be extended latter
        self.providers = ['mailgun', 'mandrill']

        # provider host list
        self.hosts = {'mailgun' :
                      "https://api.mailgun.net/v2/sandbox76a2100f2417401498f"\
                      "aff7061a2048b.mailgun.org/messages",
                      'mandrill' :
                      "https://mandrillapp.com/api/1.0/users/ping.json"}

        # list of keys for the service providers
        self.keys = {'mailgun' : "MAILGUN-KEY",
                     'mandrill': "MANDRILL-KEY"}

        # list of required fields in an email
        self.requiredFields = ['to', 'to_name', 'from',
                               'from_name', 'subject', 'body']

        # list of optional fields in an email
        self.optionalFields = ['delivery_time', 'cc', 'bcc']

        # list of email attributes to persist
        self.persistFields = ['provider', 'sent_ts'] +\
                             self.requiredFields +\
                             self.optionalFields

    # verify if the email server is running
    def get(self):
        return "Email Server is running!\n"

    # email sending service
    def post(self):
        # load config settings
        self.loadConfig()

        try:
            """
            1. load email json file
            2. check if there are duplicate fields in the email
            """
            message = json.loads(request.data,
                               object_pairs_hook=self.dupDet)

            # validate email
            validateErr = self.validateEmail(message)
            if validateErr is not None:
                return validateErr

            # process email including converting html body to plaintext
            self.processEmail(message)

            # send email
            return self.sendEmail(message)

        except Exception as e:
            return "Exception: {0}!\n".format(e)

    """
    load config json file if passed, if not, use the setting in config.py.
    Any change in config json file doesn't require a restart of the service
    without affecting the clients.
    """
    def loadConfig(self):
        global config
        # reload the config json file if passed
        if len(sys.argv) >= 2:
            fconfig = open(sys.argv[1])
            config = json.load(fconfig)
            fconfig.close()

        """
        self.provider:
           is used to dynamically pick the email service provider
        """
        if 'provider' in config.keys() and config['provider'] in self.providers:
            self.provider = config['provider']
        else:
            """
            We simply set 'mailgun' as the service provider if the configured
            provider is not 'mandrill' or not configured
            """
            self.provider = self.providers[0]

    """
    duplicate fields detection:
      raise an exception if there are duplicate fields in an email
      return a message dict otherwise
    """
    def dupDet(self, pairs):
        # message dict
        message = {}

        # list of duplicate keys
        dupKeys = []

        # loop through the pairs
        for k,v in pairs:
            if k in message:
               dupKeys.append(k)
            else:
               message[k] = v

        if dupKeys != []:
            raise ValueError("Duplicate field(s) in the email: {0}"\
                             .format(dupKeys))
        else:
            return message

    """
    validate an email:
      1. check if there are any missing required fields
      2. check if there are any unsupported fields
      3. check if the email addresses are valid
    """
    def validateEmail(self, message):
        # error message if any
        error = ""

        # check if there are missing fields that are required
        missingFields = [item for item in self.requiredFields\
                              if  item not in message.keys()]
        if missingFields != []:
            error += "  Missing field(s) {0}\n".format(missingFields)

        # check if there are un-supported fields in the email
        extraFields = [item for item in message.keys()\
                            if  item not in self.requiredFields\
                            and item not in self.optionalFields]
        if extraFields != []:
            error += "  Unsupported field(s): {0}\n".format(extraFields)

        # validate email addresses
        if not self.validEmailAddr(message['from']):
            error += "  From email address [{0}] is "\
                     "invalid\n".format(message['from'])
        if not self.validEmailAddr(message['to']):
            error += "  To email address [{0}] is "\
                     "invalid\n".format(message['to'])
        if 'cc' in message.keys()\
           and not self.validEmailAddr(message['cc']):
            error += "  cc email address [{0}] is "\
                     "invalid\n".format(message['cc'])
        if 'bcc' in message.keys()\
           and not self.validEmailAddr(message['bcc']):
            error += "  bcc email address [{0}] is "\
                     "invalid\n".format(message['bcc'])

        # send back the error message if validation fails
        if error != "":
            return "Invalid email:\n" + error

        # validation succeeds
        return None

    """
    check if an email address is valid and return
      True  -  if valid
      False -  otherwise
    """
    def validEmailAddr(self, addr):
        """
        email pattern is
           "[alphanumeric|.]+@[alphanumeric]+(.[alphanumeric]+)"

        e.g.,
           valid:    ".abc@example.com.cn", "abc@example.com"
           invalid:  ".abc@example", ".abc@example."
        """
        emailPattern = compile(r'[\w.]+@[\w]+([.][\w]+)+$')
        return (emailPattern.match(addr) is not None)

    """
    process email:
      1. convert UTC delivery time to float number
      2. convert html email body to plaintext
    """
    def processEmail(self, message):
        # convert delivery_time to seconds
        if 'delivery_time' in message.keys():
            try:
                # convert delivery_time to a float from UTC format
                message['delivery_time'] = timegm(strptime(
                                                   message['delivery_time'],
                                                   '%Y-%m-%d %H:%M:%S'))
            except Exception as e:
                raise ValueError("delivery_time format error {0}".format(e))

        # process tags with special meanings
        htmlTagMap = {'<br>' : '\n',
                      '<p>'  : '  ',
                      '</p>' : '\n'}
        for k in htmlTagMap:
            message['body'] = message['body'].replace(k, htmlTagMap[k])

        # simply remove all other tags
        htmlTag = compile(r'<[^>]+>')
        message['body'] = htmlTag.sub('', message['body'])

    """
    send email:
       provider is picked based on config file if configured,
       otherwise provider is picked based on error responses
    """
    def sendEmail(self, message):
        # number of retries if email sending fails on both service providers
        if 'retries' in config.keys():
            retries = config['retries']
        else:
            retries = 1

        # retry if all/both providers fail 
        for dummy in range(len(self.providers) * retries):
            sent = self.sendEmailVia(message, self.provider)
            if sent is None:
                # persist sent email to csv file
                if 'persist' in config.keys():
                    self.persistEmail(message, self.provider)

                # return a success message
                return "Email sent successfully via {0}!\n"\
                       .format(self.provider)
            else:
                # current provider index
                idx = self.providers.index(self.provider)

                # switch to the next provider as a cycle
                self.provider = self.providers[(idx+1) % len(self.providers)]

        # return error message
        return sent

    """
    send an email via a provider
      return error message if any
      None if successful
    """
    def sendEmailVia(self, message, provider):
        # post an email send request to the provider
        try:
            if 'timeout' in message.keys():
                timeout = message['timeout']
            else:
                timeout = None

            # send email through mailgun
            if provider == 'mailgun':
                reply = requests.post(
                         self.hosts[provider],
                         auth = ('api', self.keys[provider]),
                         data = self.mailgunPayload(message),
                         timeout = timeout)

            # send email through mandrill
            else:
                reply = requests.post(
                         self.hosts[provider],
                         data = self.mandrillPayload(message), 
                         timeout = timeout)

            # sent successfully if status code == 200
            if reply.status_code != 200:
                return "Sending email via {0} failed with status code:"\
                       " [{1}]\n".format(provider, reply.status_code)

        except Exception as e:
            return "A mail provider error occurred: {0}\n".format(e)

        # email sent successfully
        return None

    # create payload for mailgun
    def mailgunPayload(self, message):
        payload = {'from': "{0} <{1}>".format(message['from_name'],
                                              message['from']),
                   'to': ["{0} <{1}>".format(message['to_name'],
                                             message['to'])],
                   'h:Reply-To': "{0} <{1}>".format(message['from_name'],
                                                    message['from']),
                   'subject': message['subject'],
                   'text': message['body']}

        # optional email fields
        if 'cc' in message.keys():
            payload['cc'] = message['cc']
        if 'bcc' in message.keys():
            payload['bcc'] = message['bcc']
        if 'delivery_time' in message.keys():
            # mailgun uses RFC822 timestamp format
            payload['o:deliverytime'] = formatdate(message['delivery_time'])

        return payload

    # create payload for mandrill
    def mandrillPayload(self, message):
        # to email address
        toEmail =  [{'email' : message['to'],
                     'name' : message['to_name'],
                     'type' : 'to'}]

        # optional email fields
        if 'cc' in message.keys():
            toEmail =  [{'email' : message['cc'],
                         'type' : 'cc'}]
        if 'bcc' in message.keys():
            toEmail =  [{'email' : message['bcc'],
                         'type' : 'bcc'}]

        # compose the email
        msg = {'from_email': message['from'],
               'from_name': message['from_name'],
               'headers': {'Reply-To': message['from']},
               'subject': message['subject'],
               'text': message['body'],
               'to': toEmail}

        # payload to return
        payload = {}
        payload['key'] = self.keys['mandrill']
        payload['async'] = False
        payload['message'] = msg
        if 'delivery_time' in message.keys():
            # mandrill uses UTC timestamp format
            payload['send_at'] = strftime('%Y-%m-%d %H:%M:%S',
                                          gmtime(message['delivery_time']))
        return payload

    """
    Persist a sent email to the specified csv file
    The csv file can be loaded to DBMS for queries, for example MySQL

    This routine requires caller to make sure 'persist' is configured
    """
    def persistEmail(self, message, provider):
        # fill provider and sent_ts fields
        message['provider'] = provider
        message['sent_ts'] = formatdate()
        if 'delivery_time' in message.keys():
            message['delivery_time'] = formatdate(message['delivery_time'])

        # fill those non-specified fields with empty string
        for item in self.optionalFields:
            if item not in message.keys():
                message[item] = ''

        # check if this file alreay exists
        csvExist = os.path.isfile(config['persist'])

        # open and get a writer of the csv file
        csvfile = open(config['persist'], 'a')
        writer = csv.writer(csvfile)

        # csv header if needed
        if not csvExist:
            writer.writerow(self.persistFields)

        # write the sent email to csv file
        msg = [message[item] for item in self.persistFields]
        writer.writerow(msg)

        # close the file
        csvfile.close()

# log to both console and log file if requested
def logger():
    global config
    # reload the config json file if passed
    if len(sys.argv) >= 2:
        fconfig = open(sys.argv[1])
        config = json.load(fconfig)
        fconfig.close()

    # log to 'logfile'
    if 'logfile' in config.keys():
        import logging
        logging.basicConfig(
             filename=config['logfile'],
             level=logging.DEBUG, 
             format= '[%(asctime)s] %(levelname)s - %(message)s',
             datefmt='%H:%M:%S'
         )
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logging.getLogger('').addHandler(console)

if __name__ == '__main__':
    app = Flask(__name__)

    # add an email service
    app.add_url_rule('/email', view_func=Email.as_view("email server"))

    # log to file if requested
    logger()

    # run the service
    app.run()
