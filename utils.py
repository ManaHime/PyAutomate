import pyperclip

def clipboard():
    return pyperclip.paste()

def clickboard_clear():
    pyperclip.copy('')

def clipboard_copy(text):
    pyperclip.copy(text)
