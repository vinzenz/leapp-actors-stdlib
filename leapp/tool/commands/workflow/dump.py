import json
import sys

import click

from leapp.tool.commands.workflow import workflow
from leapp.tool.utils import requires_project, load_all_from, find_project_basedir


@workflow.command('dump')
@click.argument('name')
@requires_project
def cli(name):
    load_all_from(find_project_basedir('.'))
    from leapp.workflows import IPUWorkflow
    json.dump(IPUWorkflow.FactsCollectionPhase.filter.get_pre(), sys.stdout, indent=2)
    json.dump(IPUWorkflow.FactsCollectionPhase.filter.get(), sys.stdout, indent=2)
    json.dump(IPUWorkflow.FactsCollectionPhase.filter.get_post(), sys.stdout, indent=2)
