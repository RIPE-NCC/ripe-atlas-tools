import six

FORBIDDEN = dict((i, None) for i in list(range(0, 32)) + [127])


def sanitise(s, strip_newlines=True):
    """
    Strip out control characters to prevent people from screwing with the output
    """

    if not isinstance(s, six.string_types):
        return s

    if six.PY2:
        s = unicode(s)

    if not strip_newlines:
        return s.translate(
            dict((k, v) for k, v in FORBIDDEN.items() if not k == 10))

    return s.translate(FORBIDDEN)
