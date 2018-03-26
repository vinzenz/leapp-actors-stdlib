import json
import sys

from leapp.utils.clicmd import command, command_opt, command_arg
from leapp.logger import configure_logger
from leapp.tool.utils import find_project_basedir, requires_project
from leapp.tool.messages import ProjectLocalMessageAPI
from leapp.repository.scan import scan_repo


@command('run', help='Execute the given actor')
@command_arg('actor-name')
@command_opt('--save-output', is_flag=True)
@command_opt('--print-output', is_flag=True)
@requires_project
def cli(args):
    log = configure_logger()
    basedir = find_project_basedir('.')
    repository = scan_repo(basedir)
    repository.load()

    channels = ProjectLocalMessageAPI()
    channels.load()
    actor_logger = log.getChild('actors')

#    Actor.run([actor for actor in get_actors() if actor.__name__.lower() == actor_name.lower()][0](
#        channels=channels, logger=actor_logger))
    repository.lookup_actor(args.actor_name)(channels=channels, logger=actor_logger).run()

    if args.save_output:
        channels.store()
    if args.print_output:
        json.dump(channels.get_new(), sys.stdout, indent=2)
