def engineering_units(number: float) -> str:
    if abs(number) < 1e9 and abs(number) >= 1e6:
        return str(int(number)/1000000) + 'M'
    elif abs(number) < 1e6 and abs(number) >= 1e3:
        return str(int(number)/1000) + 'k'
    elif abs(number) < 1000 and abs(number) >= 1:
        return str(number)
    elif abs(number) < 1 and abs(number) >= 1e-3:
        return str(int(number*1e3)) + 'm'
    elif abs(number) < 1e-3 and abs(number) >= 1e-6:
        return str(int(number*1e6)) + 'u'
    elif abs(number) < 1e-6 and abs(number) >= 1e-9:
        return str(int(number*1e9)) + 'n'
    else:
        return None