# -*- coding: utf-8 -*-

import os

from flask_admin import Admin

from app import create_app, db
from app.models import Order, Subware, Warehouse, add_test_data
from app.model_views import WarehouseView, SubwareView, OrderView

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

admin = Admin(app, name='Warehouse Management')
admin.add_view(WarehouseView(Warehouse, db.session))
admin.add_view(SubwareView(Subware, db.session))
admin.add_view(OrderView(Order, db.session))


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Warehouse=Warehouse, Subware=Subware, Order=Order, add_test_data=add_test_data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=1)
