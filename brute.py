import sys
import utils
import plugins
import pkgutil

VALID_COMMANDS = dict()

def list_plugins():
    print("List of available plugins")
    for plugin in VALID_COMMANDS.items():
        cmd = plugin[0]
        info = plugin[1]
        print("Name: {}\nAuthor: {}\nDescription: {}\nAction: {}\n".format(info['name'], info['author'], info['description'], cmd))

# Plugin syntax check + build valid command dict
for importer, modname, ispkg in pkgutil.iter_modules(plugins.__path__):
    module = __import__("plugins.{0}.{0}".format(modname))
    my_class = getattr(module, modname.capitalize())

    if not 'CMD_NAME' in my_class.__dict__:
        print("Plugin '{}' does not have a CMD_NAME variable set. It will be disabled".format(modname))
        continue

    attack_method = hasattr(my_class, "attack")
    if not attack_method or not callable(my_class.attack):
        print("Plugin '{}' does not have the method 'attack' defined. It will be disabled".format(modname))
        continue

    plugin_info = {
        'name': modname,
        'description':  my_class.description if hasattr(my_class, "description") else None,
        'class': my_class,
        'author': my_class.author if hasattr(my_class, "author") else None
    }

    VALID_COMMANDS[my_class.CMD_NAME] = plugin_info

# Simple usage
if len(sys.argv) < 2:
    list_plugins()
    print("For more info type: python3 {} <action>".format(sys.argv[0]))
    exit(1)

# To make sure not to include the action in the argparse
action = sys.argv[1]
del sys.argv[1]

if action not in list(VALID_COMMANDS.keys()):
    print("Action '{}' not supported".format(action))
    exit(1)

plugin = VALID_COMMANDS[action]['class']()
plugin.attack()

exit(0)