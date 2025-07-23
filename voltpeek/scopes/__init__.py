from voltpeek.scopes.NS1 import NS1
from voltpeek.scopes.NS0 import NS0

def get_available_scopes(): return [{NS1.ID:NS1}, {NS0.ID:NS0}]