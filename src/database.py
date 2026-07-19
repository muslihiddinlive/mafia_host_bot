# MongoDB YO'Q - bular chindan ham vaqtinchalik ma'lumotlar (faol o'yin holati,
# navbatdagi so'rovlar, ovoz berishlar). Shuning uchun oddiy RAM'dagi (in-memory)
# mock-kolleksiyalar bilan almashtirildi - Render qayta ishga tushganda tozalanadi,
# bu MUAMMO EMAS, chunki bu ma'lumotlar soniyalar/daqiqalar davomida yashaydi.
#
# Doimiy ma'lumotlar (pul, olmos, statistika, shop, til, premium guruh) uchun
# tgdb.py (fayl + Telegram-document) ishlatiladi - bu fayl bilan aralashtirmang.
#
# Quyida stages.py/handlers.py/app.py/croco.py/gallows.py ishlatadigan MongoDB
# so'rov/yangilash operatorlarining yetarlicha to'liq qatlami: $elemMatch, $in,
# $gte, $lte, $or (so'rovlar uchun) va $set, $unset, $inc, $addToSet, $push, $pull
# (yangilashlar uchun), shu jumladan nuqtali yo'llar (masalan "players.3.alive").

import itertools
import threading
from copy import deepcopy


class ReturnDocument:
    BEFORE = 0
    AFTER = 1


def _get_path(doc, path_parts):
    """Yo'l bo'yicha ichkariga kirib (parent_container, oxirgi_kalit) qaytaradi.
    Ro'yxatga duch kelinsa, segment butun son indeksga aylantiriladi."""
    node = doc
    for part in path_parts[:-1]:
        if isinstance(node, list):
            node = node[int(part)]
        else:
            node = node.setdefault(part, {})
    return node, path_parts[-1]


def _get_value(node, key):
    if isinstance(node, list):
        index = int(key)
        return node[index] if -len(node) <= index < len(node) else None
    return node.get(key)


def _set_value(node, key, value):
    if isinstance(node, list):
        node[int(key)] = value
    else:
        node[key] = value


def _value_matches(value, condition):
    if isinstance(condition, dict) and any(k.startswith('$') for k in condition):
        for op, arg in condition.items():
            if op == '$elemMatch':
                if not isinstance(value, list) or not any(_matches(item, arg) for item in value):
                    return False
            elif op == '$in':
                if value not in arg:
                    return False
            elif op == '$gte':
                if value is None or not (value >= arg):
                    return False
            elif op == '$lte':
                if value is None or not (value <= arg):
                    return False
            else:
                return False
        return True
    return value == condition


def _field_matches(doc, path_parts, condition):
    """Nuqtali yo'l (masalan ['players', 'id']) bo'yicha tekshiradi. Yo'l davomida
    ro'yxatga duch kelinsa, Mongo'dagidek ro'yxatning ISTALGAN elementi mos kelishi
    kifoya qiladi."""
    node = doc
    for i, part in enumerate(path_parts):
        if isinstance(node, list):
            remaining = path_parts[i:]
            return any(_field_matches(item, remaining, condition) for item in node)
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return _value_matches(node, condition)


def _matches(doc, query):
    for key, condition in query.items():
        if key == '$or':
            if not any(_matches(doc, sub) for sub in condition):
                return False
            continue
        if not _field_matches(doc, key.split('.'), condition):
            return False
    return True


def _apply_update(doc, update):
    for op, changes in update.items():
        if op == '$set':
            for dotted_key, value in changes.items():
                parent, last = _get_path(doc, dotted_key.split('.'))
                _set_value(parent, last, value)
        elif op == '$unset':
            for dotted_key in changes:
                parent, last = _get_path(doc, dotted_key.split('.'))
                if isinstance(parent, dict) and last in parent:
                    del parent[last]
        elif op == '$inc':
            for dotted_key, amount in changes.items():
                parent, last = _get_path(doc, dotted_key.split('.'))
                current = _get_value(parent, last) or 0
                _set_value(parent, last, current + amount)
        elif op == '$addToSet':
            for dotted_key, value in changes.items():
                parent, last = _get_path(doc, dotted_key.split('.'))
                lst = _get_value(parent, last)
                if lst is None:
                    lst = []
                    _set_value(parent, last, lst)
                if value not in lst:
                    lst.append(value)
        elif op == '$push':
            for dotted_key, value in changes.items():
                parent, last = _get_path(doc, dotted_key.split('.'))
                lst = _get_value(parent, last)
                if lst is None:
                    lst = []
                    _set_value(parent, last, lst)
                if isinstance(value, dict) and '$each' in value:
                    lst.extend(value['$each'])
                else:
                    lst.append(value)
        elif op == '$pull':
            for dotted_key, value in changes.items():
                parent, last = _get_path(doc, dotted_key.split('.'))
                lst = _get_value(parent, last) or []
                _set_value(parent, last, [item for item in lst if item != value])


def _query_to_new_doc(query):
    """upsert paytida yangi hujjatga aylantirish uchun so'rovdan sodda (operatorsiz)
    kalit-qiymatlarni ajratib oladi."""
    doc = {}
    for key, value in query.items():
        if key.startswith('$') or '.' in key:
            continue
        if isinstance(value, dict) and any(k.startswith('$') for k in value):
            continue
        doc[key] = value
    return doc


class DeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


class MockCollection:
    def __init__(self):
        self._docs = []
        self._counter = itertools.count(1)
        self._lock = threading.RLock()

    def find_one(self, query=None):
        query = query or {}
        with self._lock:
            for doc in self._docs:
                if _matches(doc, query):
                    return deepcopy(doc)
        return None

    def find(self, query=None):
        query = query or {}
        with self._lock:
            return [deepcopy(doc) for doc in self._docs if _matches(doc, query)]

    def insert_one(self, doc):
        with self._lock:
            stored = deepcopy(doc)
            stored.setdefault('_id', next(self._counter))
            self._docs.append(stored)
        return stored

    def update_one(self, query, update, upsert=False):
        with self._lock:
            for doc in self._docs:
                if _matches(doc, query):
                    _apply_update(doc, update)
                    return
            if upsert:
                new_doc = _query_to_new_doc(query)
                new_doc.setdefault('_id', next(self._counter))
                _apply_update(new_doc, update)
                self._docs.append(new_doc)

    def find_one_and_update(self, query, update, return_document=ReturnDocument.BEFORE, upsert=False):
        with self._lock:
            for doc in self._docs:
                if _matches(doc, query):
                    before = deepcopy(doc)
                    _apply_update(doc, update)
                    return deepcopy(doc) if return_document == ReturnDocument.AFTER else before
            if upsert:
                new_doc = _query_to_new_doc(query)
                new_doc.setdefault('_id', next(self._counter))
                _apply_update(new_doc, update)
                self._docs.append(new_doc)
                return deepcopy(new_doc) if return_document == ReturnDocument.AFTER else None
        return None

    def find_one_and_delete(self, query):
        with self._lock:
            for i, doc in enumerate(self._docs):
                if _matches(doc, query):
                    return self._docs.pop(i)
        return None

    def find_and_modify(self, query, update=None, new=False, remove=False, upsert=False):
        with self._lock:
            for i, doc in enumerate(self._docs):
                if _matches(doc, query):
                    before = deepcopy(doc)
                    if remove:
                        self._docs.pop(i)
                        return before
                    if update:
                        _apply_update(doc, update)
                        return deepcopy(doc) if new else before
                    return before
            if upsert and update and not remove:
                new_doc = _query_to_new_doc(query)
                new_doc.setdefault('_id', next(self._counter))
                _apply_update(new_doc, update)
                self._docs.append(new_doc)
                return deepcopy(new_doc) if new else None
        return None

    def delete_one(self, query):
        with self._lock:
            for i, doc in enumerate(self._docs):
                if _matches(doc, query):
                    self._docs.pop(i)
                    return DeleteResult(1)
        return DeleteResult(0)

    def delete_many(self, query=None):
        query = query or {}
        with self._lock:
            before = len(self._docs)
            self._docs[:] = [doc for doc in self._docs if not _matches(doc, query)]
            return DeleteResult(before - len(self._docs))


class MockDatabase:
    def __init__(self):
        self.games = MockCollection()
        self.requests = MockCollection()
        self.polls = MockCollection()


database = MockDatabase()
