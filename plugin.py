import argparse

class Plugin:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--url", required=True)

    def build_argparse(self, parser_to_add=None):
        if parser_to_add is None:
            return self.parser

        return argparse.ArgumentParser(parents=[self.parser, parser_to_add], add_help=False)