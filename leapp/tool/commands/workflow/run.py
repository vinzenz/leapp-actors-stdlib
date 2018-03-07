from __future__ import print_function

import click

import leapp.workflows
from leapp.tool.commands.workflow import workflow
from leapp.logger import configure_logger
from leapp.tool.utils import requires_project, load_all_from, find_project_basedir


@workflow.command('runx')
@click.argument('name')
@requires_project
def cli(name):
    load_all_from(find_project_basedir('.'))
    configure_logger()
    for wf in leapp.workflows.get_workflows():
        if wf.name.lower() == name.lower():
            wf().run()
