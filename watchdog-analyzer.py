"""Watchdog Analyzer.

Usage:
  watchdog-analyzer.py (--scan <directory_path> | <path>) [--no-cache] [--no-save]
  watchdog-analyzer.py (-h | --help)

Options:
  -h --help     Show this screen.

"""

import time

from docopt import docopt

from watchdog_analyzer.dump import Dump
from watchdog_analyzer.trace import Trace
from watchdog_analyzer.viewer import Viewer


def main():
    args = docopt(__doc__)
    dump = Dump.scan_directory(args['<directory_path>']) if args['--scan'] else Dump(args['<path>'])
    tree = Trace(dump, args['--no-cache'])
    if args['--no-save'] is False:
        tree.save()

    print('Starting TUI ...')
    time.sleep(1)

    Viewer.inject_trace(tree).build().run()


if __name__ == "__main__":
    main()
