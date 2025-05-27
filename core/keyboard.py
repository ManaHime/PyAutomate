from pynput.keyboard import Controller, Key, KeyCode

keyboard = Controller()

def type(text: str):
    keyboard.type(text)

def is_modifier(k):
    return k.lower() in ['ctrl', 'alt', 'shift', 'cmd', 'win']

def get_key(k):
    k = k.lower()
    # Map win to cmd_l (left Windows key)
    if k == 'win':
        return Key.cmd_l
    try:
        return getattr(Key, k)
    except AttributeError:
        return k

def key(input_str: str):
    if input_str.startswith("[") and input_str.endswith("]"):
        keys = input_str[1:-1].split("][")
        modifiers, action_keys = [], []
        for k in keys:
            (modifiers if is_modifier(k) else action_keys).append(k)
        for mod in modifiers:
            keyboard.press(get_key(mod))
        for act in action_keys:
            k = get_key(act)
            keyboard.press(k); keyboard.release(k)
        for mod in reversed(modifiers):
            keyboard.release(get_key(mod))
    else:
        k = get_key(input_str)
        keyboard.press(k); keyboard.release(k)

def ime_on():
    keyboard.press(KeyCode.from_vk(243))
    keyboard.release(KeyCode.from_vk(244))

def ime_off():
    keyboard.press(KeyCode.from_vk(244))
    keyboard.release(KeyCode.from_vk(243))
