from my_sqlalchemy import db


class Deck_has_card(db.Model):
    __tablename__ = "deck_has_card"

    id_deck = db.Column(db.String(255), db.ForeignKey("deck.id_deck"), primary_key=True)
    id_card = db.Column(db.Integer, db.ForeignKey("card.id_card"), primary_key=True)