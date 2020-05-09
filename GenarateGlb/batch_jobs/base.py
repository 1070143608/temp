class BaseJob:
    def __init__(self, args):
        self.args = args
        self.validate_args()

    def validate_args(self):
        args_namespace = self.args._get_kwargs()
        for arg in args_namespace:
            if arg[0] in self.required_args:
                if not arg[1]:
                    raise Exception(f"argument {arg[0]} required")

