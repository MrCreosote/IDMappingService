"""
CLI tools for the ID Mapping system.
"""

from typing import List, IO
import sys
import argparse
from jgikbase.idmapping.core.util import not_none, no_Nones_in_iterable
import traceback
from pathlib import Path
from jgikbase.idmapping.builder import IDMappingBuilder
from jgikbase.idmapping.core.user_handler import LocalUserHandler


class IDMappingCLI:
    """
    The main CLI class.
    """

    _PROG = 'id_mapper'
    _USER = '--user'
    _LIST = '--list-users'

    def __init__(
            self,
            builder: IDMappingBuilder,
            args: List[str],
            stdout: IO[str],
            stderr: IO[str]
            ) -> None:
        """
        Create the CLI.

        :param args: the command line arguments without the program name.
        :param stdout: the standard out stream.
        :param stderr: the standard error stream.
        :raises TypeError: if any of the arguments are None.
        """
        not_none(builder, 'builder')
        no_Nones_in_iterable(args, 'args')
        not_none(stdout, 'stdout')
        not_none(stderr, 'stderr')
        self._builder = builder
        self._args = args
        self._stdout = stdout
        self._stderr = stderr

    def execute(self) -> int:
        """
        Run the CLI with the given arguments.

        :returns: the exit code for the program.
        """
        a = self._parse_args()
        if not a.list_users and not a.user:
            self._stderr.write('One of {} or {} must be specified.\n'.format(
                self._LIST, self._USER))
            return 1
        try:
            luh = self._builder.build_local_user_handler(Path(a.config))
        except Exception as e:
            self._handle_error(e, a.verbose)
            return 1
        if a.list_users:
            return self._list_users(luh, a.verbose)
        # ok, so user must have a value at this point
#         try:
#             u = Username(a.user)
#         except Exception as e:
#             self._handle_error(e, a.verbose)
#             return 1
#         if a.create:
#             return _create_user(luh, u, a.admin, a.verbose)
#         if a.new_token:
#             return _new_token(luh, u, a.admin, a.verbose)
#         if a.admin:
#             return _admin(luh, u, a.verbose)
        return 0

    def _list_users(self, local_user_handler: LocalUserHandler, verbose):
        try:
            users = local_user_handler.get_users()
        except Exception as e:
            self._handle_error(e, verbose)
            return 1
        self._stdout.write('* indicates an administrator:\n')
        userstr = {u.name: users[u] for u in users}   # may want to make comparable
        for u in sorted(userstr):
            admin = userstr[u]
            self._stdout.write('{}{}\n'.format(u, ' *' if admin else ''))
        return 0
#
#     def _admin(self, local_user_handler: LocalUserHandler, user: Username, admin: bool, verbose):
#         try:
#             local_user_handler.

    def _parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description='ID Mapping system CLI', prog=self._PROG,
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument(self._LIST, action='store_true',
                            help='List system users and whether they are administrators. ' +
                            'All other arguments are ignored.')
        parser.add_argument(self._USER, help='The name of the user to modify or create.')
        parser.add_argument('--create', action='store_true',
                            help='Create a user. Requires the {} option.'.format(self._USER))
        parser.add_argument('--new-token', action='store_true',
                            help='Make a new token for a user. ' +
                            'Requires the {} option. Ignored if --create is set.'.format(
                                self._USER))
        parser.add_argument('--admin', help="Set whether the user is an admin ('true') or not " +
                            "('false'). Any other values are not permitted. Requires the " +
                            '{} option.'.format(self._USER))
        parser.add_argument('--config', default='./deploy.cfg',
                            help='The location of the configuration file.')
        parser.add_argument('--verbose', action='store_true', help='Print stack trace on error.')
        return parser.parse_args(self._args)

    def _handle_error(self, exception, verbose=False):
        self._stderr.write('Error: {}\n'.format(exception.args[0]))
        if verbose:
            self._stderr.write(traceback.format_exc() + '\n')


if __name__ == '__main__':
    # manually tested
    exit(IDMappingCLI(IDMappingBuilder(), sys.argv[1:], sys.stdout, sys.stderr).execute())