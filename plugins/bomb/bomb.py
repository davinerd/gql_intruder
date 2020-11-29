# Mandatory imports
import utils
import argparse
from plugin import Plugin

# Class name matches file and folder names
class Bomb(Plugin):

  # This is mandatory
  CMD_NAME = "bomb"

  # These are optional
  author = "Davide Barbato"
  description = "Execute a nested query attack aiming at provoking a DoS"

  MAX_DEPTH = 10
  GQL_ENDPOINT = None
  QUERY = dict()

  def __init__(self):
    bomb_argparser = argparse.ArgumentParser()
    bomb_argparser.add_argument("--max-depth", type=int)
    bomb_argparser.add_argument("--query", required=True)

    bomb_argparser = self.build_argparse(bomb_argparser)
    args = bomb_argparser.parse_args()

    self.GQL_ENDPOINT = utils.parse_url(args.url)
    if self.GQL_ENDPOINT is None:
        raise Exception("URL {} is not valid!".format(args.url))

    if args.max_depth:
        self.MAX_DEPTH = args.max_depth

    self.QUERY = args.query

  # This function is mandatory.
  def attack(self):
    print("Attack!")
    print(self.MAX_DEPTH)
    print(self.QUERY)

    




