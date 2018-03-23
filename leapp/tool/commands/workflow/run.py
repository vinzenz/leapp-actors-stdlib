from __future__ import print_function

import leapp.workflows
from leapp.tool.commands.workflow import workflow
from leapp.utils.clicmd import command_arg
from leapp.logger import configure_logger
from leapp.tool.utils import requires_project, find_project_basedir
from leapp.repository.scan import scan_repo


@workflow.command('run', help='Execute a workflow with the given name')
@command_arg('name')
@requires_project
def cli(params):
    configure_logger()
    repository = scan_repo(find_project_basedir('.'))
    repository.load()
    for wf in leapp.workflows.get_workflows():
        if wf.name.lower() == params.name.lower():
            wf().run()
