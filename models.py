from peewee import (SqliteDatabase, IntegerField, DoubleField,
                    DateTimeField, datetime as peewee_datetime, Model)


db = SqliteDatabase("currency.db")


class Rate(Model):
    class Meta:
        database = db
        db_table = 'rates'
        indexes = (
            (('from_currency', 'to_currency'), True),
        )

    from_currency = IntegerField()
    to_currency = IntegerField()
    rate = DoubleField()
    updated = DateTimeField(default=peewee_datetime.datetime.now)

    def __str__(self):
        return f"Rate {self.from_currency}={self.to_currency}: {self.rate}"


def init_db():
    db.drop_tables(Rate)
    Rate.create_table()
    Rate.create(from_currency=840, to_currency=900, rate=1)
