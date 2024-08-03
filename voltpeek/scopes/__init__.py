import inspect
from voltpeek.scopes.newt_scope_one import NewtScope_One

def get_available_scopes():
    return [{NewtScope_One.ID:NewtScope_One}]