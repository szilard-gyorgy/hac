import click


class RequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.required_if = kwargs.pop('required_if')
        super(RequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        other_present  = self.required_if in opts

        if other_present:
            if not we_are_present:
                raise click.UsageError(
                    "Illegal usage: `%s` is required if `%s` is defined" % (
                        self.name, self.required_if))
            else:
                self.required = True

        return super(RequiredIf, self).handle_parse_result(ctx, opts, args)
