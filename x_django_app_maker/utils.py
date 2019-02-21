# -*- encoding: utf-8 -*-
# ! python3

def is_callable(obj):
    return hasattr(obj, '__call__')

def isAsciiString(s:str):
    return any(map(lambda c: ord(c)<256,s)) 

def xplural(value):
    return value if not isAsciiString(value) else "%ss" % value
