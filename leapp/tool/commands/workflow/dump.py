from __future__ import print_function
import json
import sys

import click

from leapp.tool.commands.workflow import workflow
from leapp.tool.utils import requires_project, load_all_from, find_project_basedir


separator = (type('Fake', (object,), {'name': '=============='})(),)


def names(p):
    return [_.name for a in p for _ in (separator + a.actors + separator if a.actors else ())]


@workflow.command('dump')
@click.argument('name')
@requires_project
def cli(name):
    load_all_from(find_project_basedir('.'))
    from leapp.workflows import IPUWorkflow
    wf = IPUWorkflow(None)
    print(wf.initial, wf.consumes, wf.produces)
    json.dump(names(wf._phase_actors), sys.stdout, indent=2)
    sys.stdout.write('\n')

