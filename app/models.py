# -*- coding: utf-8 -*-

import datetime

from . import db


class NoRoomException(Exception):
    pass


class OrderNotFoundException(Exception):
    pass


DEFAULT_COST = 10


class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    location = db.Column(db.String(64))
    subwares = db.relationship('Subware', backref='parent')

    @property
    def capacity(self):
        return sum(sw.capacity for sw in self.subwares)

    @property
    def total_goods(self):
        return sum(sw.total_goods for sw in self.subwares)

    @property
    def available_room(self):
        return self.capacity - self.total_goods

    @property
    def subwares_number(self):
        return len(self.subwares)

    def add_order(self, order):
        for subware in self.subwares:
            try:
                subware.add_order(order)
            except NoRoomException:
                pass
            else:
                break
        else:
            raise NoRoomException('Run out of capacity')

    def __repr__(self):
        return '<Warehouse, id: {}, name: {}>'.format(self.id, self.name)


class Subware(db.Model):
    __tablename__ = 'subwares'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    total_goods = db.Column(db.Integer, default=0)
    capacity = db.Column(db.Integer, default=0)
    available_room = db.Column(db.Integer)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))
    orders = db.relationship(
        'Order', backref='storage_subware')

    @property
    def available_room(self):
        return self.capacity - self.total_goods

    @property
    def location(self):
        return self.parent.location + '  ' +\
            self.parent.name + ' ' +\
            self.name

    def add_order(self, order):
        if self.available_room < 1:
            raise NoRoomException('Run out of capacity')
        order.storage_subware = self
        self.total_goods += 1
        db.session.add_all([order, self])
        db.session.commit()

    def retrieve_order(self, order):
        if order not in self.orders:
            raise OrderNotFoundException('Order not found in this subware')
        order.retrieved = True
        order.retrieve_time = datetime.datetime.now()
        self.total_goods -= 1
        db.session.add_all([order, self])
        db.session.commit()

    def __repr__(self):
        return '<Subware, id: {}, name: {}, capacity: {}, parent: {}>'.format(self.id, self.name, self.capacity, self.parent.name)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    kind_id = db.Column(db.Integer, db.ForeignKey('kinds.id'))
    description = db.Column(db.String(128))
    username = db.Column(db.String(20), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    subware_id = db.Column(db.Integer, db.ForeignKey('subwares.id'))
    retrieved = db.Column(db.Boolean, default=False)
    retrieve_time = db.Column(db.DateTime)

    @property
    def location(self):
        return self.storage_subware.parent.location + '  ' +\
            self.storage_subware.parent.name + ' ' +\
            self.storage_subware.name

    @property
    def cost(self):
        if self.retrieved == False:
            total_days = (datetime.datetime.now() - self.create_time).days + 1
        else:
            total_days = (self.retrieve_time - self.create_time).days + 1
        return self.kind.value * total_days

    def __repr__(self):
        return '<Order, id: {}, name: {}, retreived: {}>'.format(self.id, self.name, self.retrieved)


class Kind(db.Model):
    __tablename__ = 'kinds'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    value = db.Column(db.Integer, nullable=False, default=DEFAULT_COST)
    orders = db.relationship('Order', backref='kind', lazy='dynamic')

    def __repr__(self):
        return '<Kind, name: {}, value: {}>'.format(self.name, self.value)


def add_test_data():
    ware1 = Warehouse(name='BJWarehouse', location='Beijing')
    ware2 = Warehouse(name='NYWarehouse', location='WhoCares')
    ware3 = Warehouse(name='LDWarehouse', location='London')
    sub1 = Subware(name='BJ1', parent=ware1, capacity=15)
    sub2 = Subware(name='BJ2', parent=ware1, capacity=20)
    sub3 = Subware(name='NY1', parent=ware2, capacity=10)
    sub4 = Subware(name='NY2', parent=ware2, capacity=30)
    sub5 = Subware(name='LD1', parent=ware3, capacity=30)
    sub6 = Subware(name='LD2', parent=ware3, capacity=15)
    kind1 = Kind(name='other', value=10)
    kind2 = Kind(name='clothes', value=2)
    kind3 = Kind(name='furniture', value=5)
    db.session.add_all(
        [ware1, ware2, ware3, sub1, sub2, sub3, sub4, sub5, sub6, kind1, kind2, kind3])
    db.session.commit()
