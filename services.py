def hex_to_dec_list(hex_str):
    """
    Преобразует шестнадцатеричный код в список десятичных чисел.
    """
    dec_list = []
    if hex_str is not None:
        for i in range(0, len(hex_str), 2):
            dec_list.append(int(hex_str[i:i+2], 16))
    return dec_list

