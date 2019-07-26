def decapitalize(s):
    return s[0].lower() + s[1:]


def snake_to_upper_camel_case(s):
    return ''.join([word.capitalize() for word in s.split('_')])


def snake_to_camel_case(s):
    return decapitalize(snake_to_upper_camel_case(s))
