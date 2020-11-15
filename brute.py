import sys
import utils
import plugins
import pkgutil

VALID_COMMANDS = dict()

# Plugin syntax check + build valid command dict
for importer, modname, ispkg in pkgutil.iter_modules(plugins.__path__):
    module = __import__("plugins."+modname)
    my_class = getattr(module, modname.capitalize())

    if not 'CMD_NAME' in my_class.__dict__:
        print("Plugin '{}' does not have a CMD_NAME variable set. It will be disabled".format(modname))
        continue

    attack_method = hasattr(my_class, "attack")
    if not attack_method or not callable(my_class.attack):
        print("Plugin '{}' does not have the method 'attack' defined. It will be disabled".format(modname))
        continue

    VALID_COMMANDS[my_class.CMD_NAME] = dict({'class': my_class})

# To make sure not to include the action in the argparse
action = sys.argv[1]
del sys.argv[1]

if action not in list(VALID_COMMANDS.keys()):
    print("Action not supported")
    exit(1)

plugin = VALID_COMMANDS[action]['class']()
plugin.attack()

exit(0)