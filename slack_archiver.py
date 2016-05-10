#!/usr/bin/python

from datetime import timedelta, datetime
import os
import requests
import urllib3
urllib3.disable_warnings()

## script to archive channels with 0 users in them.
#good to have if you did a bad import :)


#only needed to edit here
SLACK_TOKEN = 'xoxp-.....'
#

# api_endpoint is a string, and payload is a dict
def slack_api_http_get(api_endpoint=None, payload=None):
  uri = 'https://slack.com/api/' + api_endpoint
  payload['token'] = SLACK_TOKEN
  try:
    response = requests.get(uri, params=payload)
    if response.status_code == requests.codes.ok:
      return response.json()
    else:
      raise Exception(response.content)
  except Exception as e:
    raise Exception(e)


def get_all_channels():
  payload  = {'exclude_archived': 1}
  api_endpoint = 'channels.list'
  channels = slack_api_http_get(api_endpoint=api_endpoint, payload=payload)['channels']
  all_channels = []
  for channel in channels:
    all_channels.append({'id': channel['id'], 'name': channel['name']})
  return all_channels


def get_users(channel_info):
  members = 0
  for users in channel_info['channel']['members']:
      members +=1
  return members


def get_inactive_channels(all_unarchived_channels):
  payload  = {'inclusive': 0, 'oldest': 0, 'count': 50}
  api_endpoint = 'channels.info'
  inactive_channels = []
  for channel in all_unarchived_channels:
    payload['channel'] = channel['id']
    channel_info = slack_api_http_get(api_endpoint=api_endpoint, payload=payload)
    users = get_users(channel_info)
    if users < 1:
      inactive_channels.append(channel)
  return inactive_channels


def send_channel_message(channel_id, message):
  payload  = {'channel': channel_id, 'username': 'channel_reaper', 'icon_emoji': ':ghost:', 'text': message}
  api_endpoint = 'chat.postMessage'
  slack_api_http_get(api_endpoint=api_endpoint, payload=payload)


def archive_inactive_channels(channels):
  api_endpoint = 'channels.archive'
  for channel in channels:
    send_channel_message(channel['id'], "archiving this automagically")
    payload = {'channel': channel['id']}
    slack_api_http_get(api_endpoint=api_endpoint, payload=payload)
    print "Archiving channel... %s" % channel['name']


all_unarchived_channels = get_all_channels()
inactive_channels       = get_inactive_channels(all_unarchived_channels)
archive_inactive_channels(inactive_channels)
