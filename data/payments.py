import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Payments(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'payments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    who_paid = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    pay_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    #members = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    #email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey("category.id"))

    user = orm.relation('User')
    # categories = orm.relation("Category",
    #                            secondary="association",
    #                            backref="payments")

    def __repr__(self):
        return f'<Paments> {self.id} {self.title} {self.who_paid}'
