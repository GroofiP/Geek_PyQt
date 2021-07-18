from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column, text, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker, registry, relationship

from service import log_send

PATH = "sqlite:///sqlite3.db"
DICT_TABLE = {
    "users": ["login", "information"],
    "histories_users": ["date", "ip_date"]
}


class Storage:
    def __init__(self, path, table, login=None, information=None, date=None, ip_date=None, login_recv=None):
        self.engine = create_engine(path)
        self.login = login
        self.information = information
        self.date = date
        self.ip_date = ip_date
        self.table = table
        self.metadata = MetaData()
        self.login_recv = login_recv

    def con_base(self):
        mapper_registry = registry()
        user = Table("users", self.metadata,
                     Column('id', Integer, primary_key=True, unique=True, autoincrement=True),
                     Column("login", String),
                     Column("information", String),
                     )
        history = Table("histories_users", self.metadata,
                        Column('id', Integer, primary_key=True, unique=True, autoincrement=True),
                        Column('id_user', ForeignKey("users.id")),
                        Column("date", String),
                        Column("ip_date", String),
                        )
        contacts = Table("contacts", self.metadata,
                     Column('id', Integer, primary_key=True, unique=True, autoincrement=True),
                     Column("id_send", Integer),
                     Column("id_recv", Integer, unique=True),
                     )
        if self.table == "users":
            try:
                mapper_registry.map_imperatively(User, user)
                mapper(User, user, properties={
                    'addresses': relationship(History, backref='user', order_by=history.c.id),
                    "adr": relationship(Contacts, backref='user', order_by=contacts.c.id),
                })
                mapper(History, history)
                mapper(Contacts, contacts)
            except Exception as ex:
                log_send(ex)
        elif self.table == "histories_users":
            try:
                mapper(History, history)
            except Exception as ex:
                log_send(ex)
        elif self.table == "contacts":
            try:
                mapper(Contacts, contacts)
            except Exception as ex:
                log_send(ex)

    def add_base(self):
        if self.table == "users":
            self.con_base()
            base_a = User(login=str(self.login), information=str(self.information))
        elif self.table == "histories_users":
            self.con_base()
            base_a = History(id_user=int(self.login), date=str(self.date), ip_date=str(self.ip_date))
        elif self.table == "contacts":
            self.con_base()
            base_a = Contacts(id_send=self.login, id_recv=self.login_recv)
        else:
            base_a = ""
        self.metadata.create_all(self.engine)
        session_cls = sessionmaker(bind=self.engine)
        session = session_cls()
        session.add(base_a)
        session.commit()

    def view_table(self):
        t = text("SELECT * FROM users")
        result = self.engine.connect().execute(t)
        list_result = []
        for a in result:
            print(a)
            list_result.append(a[1])
        return list_result

    def view_table_all(self):
        t = text("SELECT * FROM users")
        result = self.engine.connect().execute(t)
        return result

    def view_table_main(self, main):
        t = text("SELECT * FROM " + main)
        result = self.engine.connect().execute(t)
        return result


class User:
    def __init__(self, login, information):
        self.login = login
        self.information = information


class History:
    def __init__(self, id_user, date, ip_date):
        self.id_user = id_user
        self.date = date
        self.ip_date = ip_date


class Contacts:
    def __init__(self, id_send, id_recv):
        self.id_send = id_send
        self.id_recv = id_recv
