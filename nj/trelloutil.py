"""Trello handler utility functions"""
import os
import re
import datetime
import dateutil
import colorama
# pylint: disable=no-name-in-module
from trello import TrelloClient
from conf import *

def trello_creds():
    """Wrapper function to retrieve trello credentials"""
    return TrelloClient(
        api_key=os.environ['TRELLO_API_KEY'],
        api_secret=os.environ['TRELLO_API_SECRET'],
        token=os.environ['TRELLO_TOKEN'],
        token_secret=os.environ['TRELLO_TOKEN_SECRET']
    )

def trello_board_name():
    """Logic function to get the backlog board name or default"""

    return os.getenv('TRELLO_BACKLOG_BOARD') or TRELLO_BACKLOG_BOARD

def backlog_board():
    """Retrieve the backlog board"""

    client = trello_creds()

    backlog_boards = [_ for _ in client.list_boards() if _.name == trello_board_name()]
    if len(backlog_boards) != 1:
        raise ValueError(f'Unexpected count of boards found: {len(backlog_boards)}')

    return backlog_boards[0]

def format_due_date(card):
    """Format the due date for output"""

    local_timezone = dateutil.tz.tzlocal()
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(days=1)

    due_output = f'{colorama.Fore.BLUE}Unscheduled'
    if card.due_date:
        due_datetime = card.due_date.astimezone(local_timezone)
        hour = due_datetime.hour if due_datetime.hour <= 12 else due_datetime.hour - 12
        minute = ('0' + str(due_datetime.minute))[-2:]
        am_or_pm = 'am' if due_datetime.hour < 12 else 'pm'
        if due_datetime.date() == today.date():
            # pylint: disable=line-too-long
            due_output = f'{colorama.Style.BRIGHT}Today {hour}:{minute} {am_or_pm}{colorama.Style.NORMAL}'
        elif due_datetime.date() < today.date():
            due_output = f'{colorama.Style.BRIGHT}{colorama.Fore.RED}Past Due{colorama.Style.NORMAL}'
        elif due_datetime.date() == tomorrow.date():
            due_output = f'Tomorrow {hour}:{minute} {am_or_pm}'
        else:
            due_output = due_datetime.strftime(f'%Y-%m-%d {hour}:{minute} {am_or_pm}')
        due_output = f'{colorama.Fore.CYAN}{due_output}'
    return due_output

def parse_new_due_date(due_date):
    """Parse a new due date"""
    if not due_date:
        return

    new_due_date_hour = 17
    new_due_date_minute = 0
    new_due_date_second = 0
    new_due_date_ms = 0

    today = datetime.datetime.today()

    if due_date == 'today':
        new_due_date = today.replace(
            hour=new_due_date_hour,
            minute=new_due_date_minute,
            second=new_due_date_second,
            microsecond=new_due_date_ms
        )
        return new_due_date

    if due_date == 'tomorrow':
        new_due_date = today.replace(
            day=today.day + 1,
            hour=new_due_date_hour,
            minute=new_due_date_minute,
            second=new_due_date_second,
            microsecond=new_due_date_ms
        )
        return new_due_date

    regex_match = re.search(r'^(\d+)\s*days?$', due_date)
    if regex_match:
        new_due_date = today + datetime.timedelta(days=int(regex_match.group(1)))
        new_due_date = new_due_date.replace(
            hour=new_due_date_hour,
            minute=new_due_date_minute,
            second=new_due_date_second,
            microsecond=new_due_date_ms
        )
        return new_due_date

    regex_match = re.search(r'^(\d+)[/-](\d+)$', due_date)
    if regex_match:
        new_due_date = datetime.datetime(
            today.year,
            int(regex_match.group(1)),
            int(regex_match.group(2)),
            new_due_date_hour,
            new_due_date_minute
        )
        return new_due_date

    regex_match = re.search(r'^(\d+)[/-](\d+)[/-](\d+)$', due_date)
    if regex_match:
        new_due_date = datetime.datetime(
            int(regex_match.group(1)),
            int(regex_match.group(2)),
            int(regex_match.group(3)),
            new_due_date_hour,
            new_due_date_minute
        )
        return new_due_date
