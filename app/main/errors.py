from flask import render_template
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    # return render_template('error/404.html'), 404
    return '页面不存在', 404


@main.app_errorhandler(500)
def internal_server_error(e):
    # return render_template('error/404.html'), 500
    return '服务器错误', 500
