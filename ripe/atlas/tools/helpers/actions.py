from argparse import Action


class StoreIfNotEmpty(Action):
    """
    Like 'store' but don't overwrite an existing/conflicting option if the given
    value is empty.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            setattr(namespace, self.dest, values)
