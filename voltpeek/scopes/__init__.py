import inspect
from voltpeek.scopes.newt_scope_one import NewtScope_One
from voltpeek.scopes.AD3 import AD3

def get_available_scopes():
    return [{NewtScope_One.ID:NewtScope_One}, {AD3.ID:AD3}]