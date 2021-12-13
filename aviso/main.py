import os
import sys
import time

import praw

from prawcore.exceptions import PrawcoreException as APIException
from twilio.rest import Client

from aviso import (
  praw_config,
  get_env,
  logger,
  send_offer_alert,
  subreddits,
)


if __name__ == '__main__':
  while True:
    try:
      reddit = praw.Reddit(
        **praw_config['aviso'],
        config_settings=praw_config['DEFAULT'],
      )
      
      logger.info('Instantiated Reddit client...')
      
      sms_client = Client(get_env('TWILIO_ACCOUNT_SID'), get_env('TWILIO_AUTH_TOKEN'))

      logger.info('Instantiated Twilio client...')
      logger.info('Initialization successful. Listening for new posts...')
      print()

      subreddit = reddit.subreddit(subreddits)
      for post in subreddit.stream.submissions(skip_existing=True):
        send_offer_alert(
          sms_client,
          created_utc=post.created_utc,
          permalink=post.permalink,
          title=post.title,
        )
        
        logger.info(f'Sent alert for {post.title}...')

    except KeyboardInterrupt:
      logger.exception('Keyboard interruption received. Halting execution.')
      break

    except APIException as e:
      logger.exception(f'PRAW exception received: {str(vars(e))}')
      time.sleep(praw_config['DEFAULT']['timeout'])