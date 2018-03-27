import os

from leapp.utils.clicmd import command, command_opt


@command('', help='')
@command_opt('debug', is_flag=True, help='Enables debug logging')
@command_opt('resume', is_flag=True, help='Continue the last execution after it was stopped (e.g. after reboot)')
def main(args):
    os.environ['LEAPP_DEBUG'] = '1' if args.debug else '0'


if __name__ == "__main__":
    main()