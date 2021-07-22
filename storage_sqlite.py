from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column, text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapper, sessionmaker, registry, relationship

from service import log_send

PATH = "sqlite:///sqlite3.db"
DICT_TABLE = {
    "users": ["login", "information"],
    "histories_users": ["date", "ip_date"]
}


class Storage:
    def __init__(self, path, table, login=None, information=None, date=None, ip_date=None, login_recv=None,
                 message=None, list_conta=None):
        self.engine = create_engine(path)
        self.login = login
        self.information = information
        self.date = date
        self.ip_date = ip_date
        self.table = table
        self.metadata = MetaData()
        self.login_recv = login_recv
        self.message = message
        self.list_conta = list_conta

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
                         Column("id_recv", Integer),
                         UniqueConstraint('id_send', 'id_recv', name='uix_1')
                         )
        history_message = Table("history_message", self.metadata,
                                Column('id', Integer, primary_key=True, unique=True, autoincrement=True),
                                Column("id_send", Integer),
                                Column("message", String),
                                )
        list_contacts = Table("list_contacts", self.metadata,
                              Column('id', Integer, primary_key=True, unique=True, autoincrement=True),
                              Column("id_send", Integer),
                              Column("list_con", String),
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
        elif self.table == "history_message":
            try:
                mapper(History_Message, history_message)
            except Exception as ex:
                log_send(ex)
        elif self.table == "list_contacts":
            try:
                mapper(List_Contact, list_contacts)
            except Exception as ex:
                log_send(ex)

    def main_session(self):
        self.metadata.create_all(self.engine)
        session_cls = sessionmaker(bind=self.engine)
        return session_cls()

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
        elif self.table == "history_message":
            self.con_base()
            base_a = History_Message(id_send=self.login, message=self.message)
        elif self.table == "list_contacts":
            self.con_base()
            l_s = str(self.list_conta)
            print(type(l_s))
            base_a = List_Contact(id_send=self.login, list_con=l_s)
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

    def get_contacts(self, text_sel):
        t = text(text_sel)
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


class History_Message:
    def __init__(self, id_send, message):
        self.id_send = id_send
        self.message = message


class List_Contact:
    def __init__(self, id_send, list_con):
        self.id_send = id_send
        self.list_con = list_con


if __name__ in "__main__":
    pass
