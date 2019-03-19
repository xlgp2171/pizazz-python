""""""


def merge(config, key, mix):
    tmp = config.get(key, {})
    tmp = tmp if tmp else {}
    tmp.update(mix)
    mix.update(tmp)


def get_nested(config, def_value, *keys):
    tmp = config

    for key in keys:
        if tmp and isinstance(tmp, dict):
            tmp = tmp.get(key, def_value)
        else:
            break

    return tmp if tmp else def_value
