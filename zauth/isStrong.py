def validate_passwd(password:str):
    if len(password) < 8:
        return 'Password lenght must be greater than eight charachters'
    lowers = uppers = digits = symbols = 0
    for i in password:
        if i.isupper():
            uppers+=1
        elif i.islower():
            lowers+=1
        elif i.isdigit():
            digits+=1
        elif i.isprintable():
            symbols+=1
        else:
            return 'Password contains bad charachters `whitespace`'
    if lowers == 0 or uppers == 0 or digits == 0 or symbols == 0:
        return 'Password must contain mix of upper and lower charachter, digits, symbols'
    return 'Strong'