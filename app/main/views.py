# -*- coding: utf-8 -*-

from flask import redirect, url_for, render_template, request, jsonify

from .. import db
from ..models import Warehouse, Subware, Order, Kind, NoRoomException
from . import main


@main.route('/')
def _index():
    return redirect(url_for('.index'))


@main.route('/index')
def index():
    return render_template('index.html')


@main.route('/order')
def order():
    warehouses = [wh.name for wh in Warehouse.query.all()]
    kinds = [kd.name for kd in Kind.query.all()]
    return render_template('order.html', warehouses=warehouses, kinds=kinds)


@main.route('/retrieve')
def retrieve():
    return render_template('retrieve.html')


@main.route('/ajax/create_order', methods=['GET', 'POST'])
def ajax_create_order():
    name = request.form['name']
    if len(name) == 0:
        return jsonify({'status': False, 'message': 'Order name is required.'})
    if len(name) > 20:
        return jsonify({'status': False, 'message': 'Order name is too long. It should be less than 20 letters.'})
    username = request.form['username']
    if len(username) == 0:
        return jsonify({'status': False, 'message': 'Your name is required.'})
    if len(username) > 20:
        return jsonify({'status': False, 'message': 'Your name is too long. It should be less than 20 letters.'})
    kind = Kind.query.filter_by(name=request.form['kind']).first()
    description = request.form['description']
    warehouse = Warehouse.query.filter_by(name=request.form['wh_name']).first()
    try:
        order = Order(name=name, description=description,
                      username=username, kind=kind)
        warehouse.add_order(order)
        receipts = username + '_' + name + '.txt'
        with open('app/static/receipts/' + receipts, 'w') as f:
            f.write('Reiceit\nOrder id: {}\nOrder name: {}\nUser name: {}\nCreate Time: {}'.format(
                order.id, order.name, order.username, order.create_time))
        return jsonify({'status': True, 'message': 'Submit order successfully.\nPlease remember your order id: {}'.format(order.id), 'url': '/static/receipts/' + receipts})
    except NoRoomException as err:
        return jsonify({'status': False, 'message': 'Operation failed, reason: ' + str(err)})


@main.route('/ajax/retrieve_order', methods=['GET', 'POST'])
def ajax_retrive_order():
    operation = request.args['operation']
    order_id = request.form['oid']
    username = request.form['username']
    if not username:
        return jsonify({'status': False, 'message': 'Your name is required.'})
    try:
        order_id = int(order_id)
    except:
        return jsonify({'status': False, 'message': 'Wrong input of order id.'})
    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({'status': False, 'message': 'Order doesn\'t exist.'})
    if username != order.username:
        return jsonify({'status': False, 'message': 'Your name does not correspond to the order.'})
    if order.retrieved:
        message = 'Order has been retrieved.\nName: {}\nKind: {}\nDescription: {}\nCreate time: {}\nRetrieve time: {}\nLocation: {}\nCost: {}\n'.format(
            order.name, order.kind.name, order.description, order.create_time, order.retrieve_time, order.location, order.cost)
        return jsonify({'status': False, 'message': message})
    if operation == 'check':
        message = 'Name: {}\nKind: {}\nDescription: {}\nCreate time: {}\nLocation: {}\nCost till now: {}\n'.format(
            order.name, order.kind.name, order.description, order.create_time, order.location, order.cost)
        return jsonify({'status': True, 'message': message})
    elif operation == 'retrieve':
        order.storage_subware.retrieve_order(order)
        return jsonify({'status': True, 'message': 'Retrieve successfully\nTotal cost: {}'.format(order.cost)})


@main.route('/admin/ajax/check_details')
def ajax_check_details():
    changes = []
    for warehouse in Warehouse.query.all():
        for subware in warehouse.subwares:
            total_goods = sum(1 for od in subware.orders if not od.retrieved)
            if total_goods != subware.total_goods:
                subware.total_goods = total_goods
                changes.append(subware)
    try:
        db.session.add_all(changes)
        db.session.commit()
        return jsonify({'status': True, 'message': 'Operation success. Total changes: {}'.format(len(changes))})
    except Exception as err:
        return jsonify({'status': False, 'message': 'Operation fail, reason: ' + str(err)})
