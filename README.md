# GraphQL Intruder
Plugin oriented tool to perform GraphQL endpoint vulnerability assessment.

# Usage
Plugins are listed in their own folders under `plugins` folder.

To list all the available plugins:
```
$ python3 brute.py
List of available plugins
Name: dump
Author: Davide Barbato
Description: Dump GraphQL schema via introspection.
Action: dump

Name: intruder
Author: Davide Barbato
Description: Simple bruteforce inspired by Burp Suite Intruder.
Action: intruder

For more info type: python3 brute.py <action>
```

# How to write a plugin
Writing a plugin is pretty simple:
1. Create a folder under `plugins`. The folder's name reflects the file and class name. Example:
```
plugins/
├── newplugin
│   ├── newplugin.py
│   ├── __init__.py
``` 

2. Write your plugin. Inside `newplugin.py`:
```
# Mandatory imports
import utils
import argparse
from plugin import Plugin

# Class name matches file and folder names
class Newplugin(Plugin):

  # This is mandatory
  CMD_NAME = "new_attack"

  # These are optional
  author = "Davide Barbato"
  description = "Super duper new attack plugin"
  
  def __init__(self):
    # The Plugin class' argparse already sets the URL as mandatory parameter.
    # If you need to add your own parser, do it and call self.build_argparse(your_new_parser)
    parser = self.build_argparse()
    args = parser.parse_args()

  # This function is mandatory.
  def attack(self):
    print("Attack!")
```

3. Add the module to `plugins/__init__.py`:
```
from plugins.intruder.intruder import Intruder
from plugins.dump.dump import Dump
from plugins.newplugin.newplugin import Newplugin
```

4. Enjoy

