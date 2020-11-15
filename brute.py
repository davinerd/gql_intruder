import sys
import utils
import plugins
import pkgutil


#def build_argparse(parse_to_add):
#    return argparse.ArgumentParser(parents=[main_parser, parse_to_add], add_help=False)


VALID_COMMANDS = dict()
action = sys.argv[1]
del sys.argv[1]


for importer, modname, ispkg in pkgutil.iter_modules(plugins.__path__):
    module = __import__("plugins."+modname)
    my_class = getattr(module, modname.capitalize())
    VALID_COMMANDS[my_class.CMD_NAME] = dict({'class': my_class})

if action not in list(VALID_COMMANDS.keys()):
    print("Action not supported")
    exit(1)

plugin = VALID_COMMANDS[action]['class']()
plugin.attack()

exit()