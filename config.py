# config file
global config

# all of the following fields are optional
config = {
    # email service provider:
    #    ''         :  default value, a provider is dynamically selected
    #                  based on their error responses
    #    'mailgun'  :  use Mailgun as the provider
    #    'mandrill' :  use Mandrill as the provider
    'provider' : 'mailgun',

    # timeout (in seconds) for post request to the email service provider
    'timeout'  : 5,

    # max number of retries if email sending fail on both service providers
    'retries'  : 2,

    # persist the sent emails to a csv file which may be loaded to DBMS
    'persist'  : 'emailSent.csv',

    # logfile is specified if one wants to log DEBUG level logs to a file
    'logfile'  : 'emailServer.log'
}
