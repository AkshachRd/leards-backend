from models.deck import Deck
from models.user import User
from models.user_has_deck import UserHasDeck


def fetch_model(user):
    model = {
        'user': {
            'id': user.id_user,
            'name': user.username,
            'email': user.email,
            'profileImage': 'https://images-ext-2.discordapp.net/external/_JtzjmdL5US9Fx2SoC_CCovQEwadWq_Zj3SYASN6ihw/https/i.ibb.co/DR067K7/Group-241-1.png%27'
        },
        'dataState': {
            'currentGroupId': 'root',
            'rootGroup': {
                'id': 'root',
                'parentId': 'root',
                'name': 'decks',
                'img': '',
                'content': []
            }
        }
    }

    user_decks = UserHasDeck.query.filter_by(id_user=user.id_user).all()
    for user_deck in user_decks:
        model['dataState']['rootGroup']['content'].append(extract_deck(user_deck.id_deck, 'root'))

    return model


def extract_deck(id_deck, id_parent_deck):
    """

    :param id_parent_deck:
    :param id_deck:
    :return: Dictionary with full deck info
    """
    deck = Deck.query.get(id_deck)
    model_deck = {
        'id': id_deck,
        'parentId': id_parent_deck,
        'name': '',
        'img': '',
        'content': []
    }

    return deck


def extract_card():
    return 0


def test():
    return User.query.get(1)