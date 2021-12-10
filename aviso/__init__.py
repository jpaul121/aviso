import configparser
import json
import logging
import os
import sys

from datetime import datetime
from dotenv import load_dotenv
from logging.config import fileConfig as logging_config

from twilio.base.exceptions import TwilioRestException


LOGGING_CONFIG_FILE = 'logging_config.ini'
ENV_FILE = '.env'
PRAW_CONFIG_FILE = 'praw.ini'
SUBREDDIT_FILE = 'subs.json'


def get_env(env_key):
  """ Get environment variables, or throw an error. """
  
  load_dotenv(
    os.path.join(os.path.dirname(__file__), '.env'),
  )

  try:
    return os.getenv(env_key)
  except Exception as e:
    return e


def send_offer_alert(sms_client, **kwargs):
  """ Helper function for using the Twilio API. """
  
  if not 'permalink' in kwargs:
    raise ValueError('Link to offer not received.')
  
  created_utc = kwargs.get('created_utc', datetime.now())
  title = kwargs.get('title', 'Untitled')
  
  body_text = f"""
  {title}\n
  https://reddit.com/{permalink}/
  Posted on {datetime.utcfromtimestamp(created_utc).strftime('%m/%d at %H/%M.')}\n
  """
  
  try:
    sms_client.messages.create(
      from_=get_env('TWILIO_PHONE_NUMBER'),
      to=get_env('PERSONAL_PHONE_NUMBER'),
      body=body_text,
    )
  
  except TwilioRestException:
    logging.warning('Link to offer not received. Aborting SMS delivery.')


assert os.path.isfile(LOGGING_CONFIG_FILE)
assert os.path.isfile(ENV_FILE)
assert os.path.isfile(PRAW_CONFIG_FILE)
assert os.path.isfile(SUBREDDIT_FILE)

logging_config('logging_config.ini')
logger = logging.getLogger(__name__)

logger.info('Started bot...')

try:
  praw_config = configparser.ConfigParser(os.environ)
  praw_config.read(PRAW_CONFIG_FILE)

  environment = get_env('ENV')

  logger.info(f'Running on environment: {environment}')

  with open(SUBREDDIT_FILE, 'r') as subs:
    if environment == 'TEST':
      pass
    elif environment == 'PROD':
      json_raw = json.load(subs)
      subreddits = '+'.join(json_raw)
    else:
      raise ValueError('ENV variable must be either \'TEST\' or \'PROD\'.')
  
  sub_count = subreddits.count('+') + 1
  
  logger.info(f'Loaded {sub_count} subreddit(s)...')

except Exception as e:
  logger.exception(f'Could not get environment variable(s): {str(vars(e))}')