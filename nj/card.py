"""Card functionality"""
import dateutil
from datetime import datetime
import colorama
from label import parse_labels
from trelloutil import format_due_date, backlog_board, parse_new_due_date, CARD_ID_POSTFIX_COUNT
from worklist import sort_list

def card_by_id(card_id_postfix, board):
    """Retrieve a card by the last few digits of its id"""

    found_cards = [
        _ for _ in board.get_cards()
        if _.id[-CARD_ID_POSTFIX_COUNT:] == card_id_postfix
    ]

    if not found_cards:
        return
    elif len(found_cards) > 1:
        print(f'{colorama.Fore.RED}More than one card unexpectedly found{colorama.Fore.RESET}')
        return

    return found_cards[0]

def arg_show(cli_args):
    """Show a card summary"""

    board = backlog_board()

    card = card_by_id(cli_args.card_id, board)

    if not card:
        return

    print(f'{colorama.Fore.YELLOW}{colorama.Style.BRIGHT}{card.name}{colorama.Fore.RESET}')
    print(f'Due: {format_due_date(card)}{colorama.Fore.RESET}{colorama.Style.NORMAL}')

    for comment in sorted(card.get_comments(), key=lambda c: c['date'], reverse=True):
        comment_datetime = str(dateutil.parser.parse(comment['date']))
        print(f'{colorama.Fore.BLUE}{comment_datetime}', end=' ')
        print(f'{colorama.Fore.GREEN}{comment["data"]["text"]}')
        print(colorama.Fore.RESET, end='')

def arg_move(cli_args):
    """Move a card to a new list"""

    board = backlog_board()

    try:
        destination_list = [_ for _ in board.list_lists() if _.name == cli_args.list_name][0]
    except IndexError:
        print(f'{colorama.Fore.RED}Destination list not found')
        return

    card = card_by_id(cli_args.card_id, board)
    if not card:
        print(f'{colorama.Fore.RED}Card not found')
        return

    card.change_list(destination_list.id)

def arg_comment(cli_args):
    """Add a comment to a card"""

    board = backlog_board()

    card = card_by_id(cli_args.card_id, board)

    card.comment(cli_args.comment)

def arg_modify(cli_args):
    """Modify an existing card"""

    board = backlog_board()

    card = card_by_id(cli_args.card_id, board)

    if cli_args.remove_due:
        card.remove_due()

    if cli_args.remove_label:
        label_to_remove = [_ for _ in card.labels if _.name == cli_args.remove_label]
        if label_to_remove:
            card.remove_label(label_to_remove[0])

    if cli_args.label:
        add_labels = parse_labels(cli_args.label)
        if add_labels:
            card.add_label(add_labels[0])

    if cli_args.due:
        new_due = str(parse_new_due_date(cli_args.due))
        # set_due() expects the due date in a datetime object
        new_due = datetime.strptime(new_due, '%Y-%m-%d %H:%M:%S')
        card.set_due(new_due)

def arg_add(cli_args):
    """Add a new card to a given list"""

    try:
        destination_list = [
            _ for _ in backlog_board().list_lists()
            if _.name == cli_args.list_name
        ][0]
    except IndexError:
        print(f'{colorama.Fore.RED}Error searching for list')
        return

    new_due = str(parse_new_due_date(cli_args.due))

    add_labels = None
    if cli_args.labels:
        add_labels = parse_labels(cli_args.labels)

    destination_list.add_card(
        name=cli_args.card_name,
        due=new_due if cli_args.due else "null",
        labels=add_labels
    )

    sort_list(destination_list)
