import os

import click

from leapp.tool.commands.workflow import workflow
from leapp.tool.utils import find_project_basedir, requires_project, make_class_name, make_name


@workflow.command('new')
@click.argument('name')
@click.option('-s', '--short', 'short_name')
@click.option('-c', '--class', 'class_name')
@requires_project
def cli(name, short_name, class_name):
    base_dir = find_project_basedir('.')
    workflows_dir = os.path.join(base_dir, 'workflows')

    class_name = class_name or make_class_name(name)
    short_name = short_name or make_name(name)

    if not os.path.exists(workflows_dir):
        os.mkdir(workflows_dir)

    workflow_path = os.path.join(workflows_dir, make_name(name) + '.py')
    if not os.path.exists(workflow_path):
        with open(workflow_path, 'w') as f:
            f.write("""from leapp.workflows import Workflow, Phase, Flags, Filter, Policies
from leapp.tags import FactsTag, {workflow_class}Tag, CommonFactsTag, ChecksTag, CommonChecksTag


class {workflow_class}Workflow(Workflow):
    name = '{workflow_name}'
    tag =  {workflow_class}Tag
    short_name = '{workflow_short_name}'
    description = '''No description has been provided for the {workflow_name} workflow.'''

    class FactsCollection(Phase):
        name = 'Facts collection'
        filter = Filter(
            tags=(({workflow_class}Tag, FactsTag),
                  (CommonFactsTag,)))
        policies = Policies(
            error=Policies.Errors.FailPhase,
            retry=Policies.Retry.Phase)
        flags = Flags()

    class Checks(Phase):
        name = 'Checks'
        filter = Filter(
            tags=(({workflow_class}Tag, ChecksTag),
                   (CommonChecksTag,)))
        policies = Policies(
            error=Policies.Errors.FailPhase,
            retry=Policies.Retry.Phase)
        flags = Flags()
""".format(workflow_name=name, workflow_class=class_name, workflow_short_name=short_name))
