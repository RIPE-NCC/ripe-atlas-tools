import six

FORBIDDEN = dict((i, None) for i in list(range(0, 32) + [127]))


def sanitise(s, strip_newlines=True):
    """
    Strip out control characters to prevent people from screwing with the output
    """
    if six.PY2:
        s = unicode(s)
    if not strip_newlines:
        return s.translate(
            dict((j, None) for j in FORBIDDEN.keys() if not j == 10))
    return s.translate(FORBIDDEN)
