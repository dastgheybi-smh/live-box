from json import load, dump, loads, dumps
from json.decoder import JSONDecodeError
from os.path import exists
from io import BytesIO


TEMPLATE = [
    {
        "is_sql": True,
        "version": "1.0.0",
        "tables": {}
    },
    {}
]

class DBObject:
    def __init__(self, value, columns, table):
        self._value = value
        self._columns = columns
        self._table = table

    def __str__(self):
        return self._value

    @property
    def id(self):
        return list(self._value.keys())[0]


    @property
    def data(self):
        value = self._value[self.id]
        key = self._columns
        send = {}
        for k, v in zip(key, value):
            send.update({k: v})
        return send

    @property
    def db_row(self):
        return {self.id: self._value[self.id]}

    def update(self, **kwargs):
        for k in kwargs.keys():
            if k not in self._columns:
                raise KeyError(k)
        for k, v in kwargs.items():
            translate = self._columns.index(k)
            self._value[self.id][translate] = v
        self._table._update(self)

    def __len__(self):
        return len(self._value)

    def delete(self):
        self._table.db._connect()
        self._table.db.db[self._table.name].pop(self.id)
        self._table.db._save()




class Table:
    def __init__(self, db, name):
        self.db = db
        self.name = name

    def create(self, **columns) -> DBObject | None:
        table = self.name
        self.db._connect()
        if set(columns.keys()) != set(self.db.db_meta["tables"][table]):
            raise ValueError(
                f"You must have \"{len(self.db.db_meta["tables"][table])}\" columns in \"{table}\" but you give \"{len(columns.keys())}\" columns")
        else:
            if len(self.db.db[table].keys()) == 0:
                id_ = 1
            else:
                id_ = int(list(self.db.db[table].keys())[-1]) + 1
            indexes = self.db.db_meta["tables"][table]
            send = [None for _ in indexes]
            for column in columns.keys():
                send[indexes.index(column)] = columns[column]
            self.db.db[table][str(id_)] = send
            self.db._save()
            return DBObject({id_: send}, self.db.db_meta["tables"][self.name], self)

    def filter(self, **kwargs) -> list[DBObject] :
        self.db._connect()
        columns = self.db.db_meta["tables"][self.name]
        for k in kwargs.keys():
            if not ( k in columns or k == "pk"):
                raise ValueError(f"\"{k}\" is not a valid column")
        send = self.db.db[self.name].copy()
        new_send = self.db.db[self.name].copy()
        for k, v in kwargs.items():
            if k == "pk":get_pk = True
            else:get_pk = False; translate = self.db.db_meta["tables"][self.name].index(k)
            for k_, v_ in send.items():
                if get_pk:
                    if k_ != str(kwargs.get(k)):
                        new_send.pop(k_)
                elif send[k_][translate] != v:
                    new_send.pop(k_)
            send = new_send.copy()
        ret = []
        for k, v in send.items():
            ret.append(DBObject({k: v}, self.db.db_meta["tables"][self.name], self))
        return ret

    def get(self, **kwargs) -> DBObject:
        value = self.filter(**kwargs)
        if len(value) != 1:
            raise ValueError(f"get() must return exactly 1 value, but {len(value)} found")
        return value[0]

    def update(self, obj:DBObject, **kwargs) -> None:
        obj.update(**kwargs)
        self.db._connect()
        self.db.db[self.name].update(obj.db_row)
        self.db._save()

    def _update(self, obj:DBObject) -> None:
        self.db._connect()
        self.db.db[self.name].update(obj.db_row)
        self.db._save()

class DB:
    def __init__(self, db_path):
        self.db = None
        self.db_meta = None
        self.db_path = db_path
        self.pm = False
        make_db = False

        if not exists(self.db_path):
            with open(self.db_path, "w") as f:
                f.write("")
                make_db = True

        with open(db_path, 'r', encoding='utf-8') as f:
            try:
                if len(load(f)) != 2 and not load(f)[0].get("is_sql"):
                    make_db = True
            except JSONDecodeError:
                make_db = True
        if make_db:
            self.db_meta = TEMPLATE[0]
            self.db = TEMPLATE[1]
            with open(db_path, 'w', encoding='utf-8') as f:
                dump(TEMPLATE, f)
        else:
            with open(db_path, 'r', encoding='utf-8') as f:
                template = load(f)
                self.db_meta = template[0]
                self.db = template[1]
        if self.db_meta["version"] != TEMPLATE[0]["version"]:
            update = input("Your db version is different. make db again? (y/n): ")
            update = update.strip().lower()
            if update == "y":
                self.db_meta = TEMPLATE[0]
                self.db = TEMPLATE[1]
                self._save()
            elif update == "n":
                exit(0)
            else:
                exit(1)

    def premake(self):
        self.pm = True

    def remake_db(self, are_you_sure=False):
        if are_you_sure:
            self.db_meta = TEMPLATE[0]
            self.db = TEMPLATE[1]
            with open(self.db_path, 'w', encoding='utf-8') as f:
                dump(TEMPLATE, f)

    def create_table(self, name:str, columns:list) -> Table:
        self._connect()
        if not name in self.db_meta["tables"].keys():
            self._connect()
            self.db_meta["tables"][name] = columns
            self.db[name] = {}
            self._save()
        return Table(self, name)

    def table(self, name:str) -> Table | None:
        self._connect()
        if name in list(self.db_meta["tables"].keys()):
            return Table(self, name)
        raise NameError(f"Table {name} does not exist")

    def _connect(self):
        with open(self.db_path, 'r', encoding='utf-8') as f:
            template = load(f)
            self.db_meta = template[0]
            self.db = template[1]

    def _save(self):
        with open(self.db_path, 'w', encoding='utf-8') as f:
            send = [self.db_meta, self.db]
            dump(send, f)

class ByStrDB:
    def __init__(self, db_var):
        self.db = None
        self.db_meta = None
        self.db_var = db_var
        self.pm = False
        make_db = False

        try:
            res = loads(db_var)
            if len(res) != 2 and not res[0].get("is_sql"):
                make_db = True
        except JSONDecodeError:
            make_db = True
        if make_db:
            self.db_meta = TEMPLATE[0]
            self.db = TEMPLATE[1]
            self.db_var = dumps(TEMPLATE)
            self._save()
        else:
            template = loads(db_var)
            self.db_meta = template[0]
            self.db = template[1]
        if self.db_meta["version"] != TEMPLATE[0]["version"]:
            update = input("Your db version is different. make db again? (y/n): ")
            update = update.strip().lower()
            if update == "y":
                self.db_meta = TEMPLATE[0]
                self.db = TEMPLATE[1]
                self._save()
            elif update == "n":
                exit(0)
            else:
                exit(1)

    def premake(self):
        self.pm = True

    def remake_db(self, are_you_sure=False):
        if are_you_sure:
            self.db_meta = TEMPLATE[0]
            self.db = TEMPLATE[1]
            self._save()

    def create_table(self, name: str, columns: list) -> Table:
        self._connect()
        if not name in self.db_meta["tables"].keys():
            self._connect()
            self.db_meta["tables"][name] = columns
            self.db[name] = {}
            self._save()
        return Table(self, name)

    def table(self, name: str) -> Table | None:
        self._connect()
        if name in list(self.db_meta["tables"].keys()):
            return Table(self, name)
        raise NameError(f"Table {name} does not exist")

    def _connect(self):
        template = loads(self.db_var)
        self.db_meta = template[0]
        self.db = template[1]

    def _save(self):
        send = [self.db_meta, self.db]
        self.db_var = dumps(send)

class S3DB(ByStrDB):
    def __init__(self, db_path:str, cli, name):
        self.cli = cli
        self.NAME = name
        resp = cli.get_object(Bucket=name, Key=db_path)
        resp = resp["Body"].read().decode("utf-8")
        self.db_s3 = db_path
        super().__init__(resp)

    def _save(self):
        super()._save()
        req_ctx = BytesIO(self.db_var.encode("utf-8"))
        self.cli.upload_fileobj(req_ctx, self.NAME, self.db_s3)

    def _connect(self):
        self.db_var = self.cli.get_object(Bucket=self.NAME, Key=self.db_s3)
        self.db_var = self.db_var["Body"].read().decode("utf-8")
        super()._connect()