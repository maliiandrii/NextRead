from flask import Blueprint

borrowings = Blueprint('borrowings', __name__)

from app.borrowings import routes
