from flask import render_template
from werkzeug.exceptions import NotFound

def show_404_page(error):
    msg = error.description
    return render_template('404.html', msg=msg), 404
