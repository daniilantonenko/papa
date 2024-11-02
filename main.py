from utils import load_json
from parser import *

# Load new data to database
j = load_json('data.json')
save_to_database(j)

scan_all()