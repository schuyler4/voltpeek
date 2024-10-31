def engineering_units(number: float) -> str:
    if number < 1e9 and number >= 1e6:
        return str(int(number)/1000000) + 'M'
    elif number < 1e6 and number >= 1e3:
        return str(int(number)/1000) + 'k'
    elif number < 1000 and number >= 1:
        return str(number)
    elif number < 1 and number >= 1e-3:
        return str(int(number*1e3)) + 'm'
    elif number < 1e-3 and number >= 1e-6:
        return str(int(number*1e6)) + 'u'
    elif number < 1e-6 and number >= 1e-9:
        return str(int(number*1e9)) + 'n'
    else:
        return None