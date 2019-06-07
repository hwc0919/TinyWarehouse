# -*- coding: utf-8 -*-

from flask_admin.contrib.sqla import ModelView


class WarehouseView(ModelView):
    page_size = 50
    column_list = ['name', 'total_goods', 'available_room',
                   'capacity', 'location', 'subwares_number']
    column_labels = {'total_goods': 'In Stock', 'available_room': 'Available'}
    column_searchable_list = ['name', 'location']


class SubwareView(ModelView):
    page_size = 50

    column_list = ['name', 'total_goods',
                   'available_room', 'capacity', 'location']
    column_labels = {'available_room': 'Available',
                     'total_goods': 'In Stock', 'orders': 'Orders',
                     'parent.name': 'Parent', 'parent.location': 'Location'}
    form_excluded_columns = ['orders', 'total_goods']
    column_searchable_list = ['name', 'parent.name', 'parent.location']
    column_filters = ['capacity']


class OrderView(ModelView):
    can_create = False
    can_delete = False
    can_export = True
    page_size = 50
    column_exclude_list = []
    can_view_details = True

    column_list = ['id', 'name', 'username', 'create_time', 'retrieved',
                   'retrieved_time', 'location', 'kind.name', 'kind.value']
    column_labels = {'kind.name': 'Kind',
                     'kind.value': 'cost/day', 'storage_subware.name': 'Subware'}
    column_searchable_list = ['name', 'username']
    column_filters = ['kind.name', 'retrieved',
                      'create_time', 'retrieve_time', 'storage_subware.name']
    form_excluded_columns = ['create_time',
                             'retrieve_time', 'username', 'retrieved']
