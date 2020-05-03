import boto3
import datetime

class bcolors:

    colors = {'HEADER': '\033[95m',
              'OKBLUE': '\033[94m',
              'OKGREEN': '\033[92m',
              'WARNING': '\033[93m',
              'FAIL': '\033[91m',
              'ENDC': '\033[0m',
              'BOLD': '\033[1m',
              'UNDERLINE': '\033[4m'}

def check_aws_profile():

    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        credentials = credentials.get_frozen_credentials()
        return credentials.access_key, credentials.secret_key, session.region_name
    except Exception as e:
        message = "You must configure awscli before use this script.\nError: {0}".format(str(e))
        exit_critical(message)

def exit_critical(message):
    print(bcolors.colors.get('FAIL'), message, bcolors.colors.get('ENDC'), sep="")
    raise SystemExit

def message_handler(message, position):
    print(bcolors.colors.get(position), message, bcolors.colors.get('ENDC'), sep="")

def datetime_to_string(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()