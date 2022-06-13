import argparse
import logging
import os
import pwd
from sys import argv
from argparse import ArgumentTypeError
from typing import Callable


from aiohttp.web import run_app
from aiomisc import bind_socket
from aiomisc.log import LogFormat, basic_config
from configargparse import ArgumentParser
from setproctitle import setproctitle
from yarl import URL

from market.utils.pg import DEFAULT_PG_URL



ENV_VAR_PREFIX = 'MARKET_'



def validate(type: Callable, constrain: Callable):
    def wrapper(value):
        value = type(value)
        if not constrain(value):
            raise ArgumentTypeError
        return value

    return wrapper


positive = validate(int, constrain=lambda x: x > 0)


def clear_environ(rule: Callable):
    """
    Очищает переменные окружения, переменные для очистки определяет переданная
    функция rule.
    """
    # Ключи из os.environ копируются в новый tuple, чтобы не менять объект
    # os.environ во время итерации.
    for name in filter(rule, tuple(os.environ)):
        os.environ.pop(name)


parser = ArgumentParser(
    auto_env_var_prefix=ENV_VAR_PREFIX, allow_abbrev=False,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('--user', required=False, type=pwd.getpwnam,
                    help='Change process UID')

group = parser.add_argument_group('API Options')
group.add_argument('--api-address', default='10.21.0.129',
                   help='IPv4/IPv6 address API server would listen on')
group.add_argument('--api-port', type=positive, default=8081,
                   help='TCP port API server would listen on')

group = parser.add_argument_group('PostgreSQL options')
group.add_argument('--pg-url', type=URL, default=URL(DEFAULT_PG_URL),
                   help='URL to use to connect to the database')
group.add_argument('--pg-pool-min-size', type=int, default=10,
                   help='Minimum database connections')
group.add_argument('--pg-pool-max-size', type=int, default=10,
                   help='Maximum database connections')

group = parser.add_argument_group('Logging options')
group.add_argument('--log-level', default='info',
                   choices=('debug', 'info', 'warning', 'error', 'fatal'))
group.add_argument('--log-format', choices=LogFormat.choices(),
                   default='color')


def main():
    args = parser.parse_args()
    #очистка окружения
    clear_environ(lambda i: i.startswith(ENV_VAR_PREFIX))
    #настройка буфферизации
    basic_config(args.log_level, args.log_format, buffered=True)
    sock = bind_socket(address=args.api_address, port=args.api_port,
                       proto_name='http')

    if args.user is not None:
        logging.info('Changing user to %r', args.user.pw_name)
        os.setgid(args.user.pw_gid)
        os.setuid(args.user.pw_uid)

    setproctitle(os.path.basename(argv[0]))

    app = create_app(args)
    run_app(app, sock=sock)


if __name__ == '__main__':
    main()

