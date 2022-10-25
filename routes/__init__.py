from flask import Blueprint
myroutes = Blueprint('routes', __name__)

from .ui import *
from .api import *
from .admin import *
from .main_route import *
