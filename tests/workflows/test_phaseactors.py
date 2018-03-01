import pytest

from leapp.exceptions import CyclingDependenciesError
from leapp.actors import Actor
from leapp.tags import Tag
from leapp.models import Model
from leapp.channels import Channel
from leapp.workflows.phaseactors import PhaseActors


class CycleTag1(Tag):
    name = 'cycle1'


class PhaseActorsModelsTag1(Tag):
    name = 'phase-actor-models1'


class CycleChannel(Channel):
    name = 'cycle'


class CycleModel1(Model):
    channel = CycleChannel


class CycleModel2(Model):
    channel = CycleChannel


class CycleActor1(Actor):
    name = 'CycleActor1'
    consumes = (CycleModel1,)
    produces = (CycleModel2,)
    tags = (CycleTag1,)


class CycleActor2(Actor):
    name = 'CycleActor2'
    consumes = (CycleModel2,)
    produces = (CycleModel1,)
    tags = (CycleTag1, PhaseActorsModelsTag1)


class CycleActor3(Actor):
    name = 'CycleActor3'
    consumes = (CycleModel1,)
    produces = ()
    tags = (CycleTag1, PhaseActorsModelsTag1)


def test_actor_phases_detect_cycles():
    # Expected a cycle to be detected
    with pytest.raises(CyclingDependenciesError):
        PhaseActors(CycleTag1.actors)

    # This should not cause a cycle to be present
    PhaseActors(PhaseActorsModelsTag1.actors)


def test_actor_phases_check_models():
    phase_actors = PhaseActors(PhaseActorsModelsTag1.actors)
    assert len(phase_actors.initial) == 1 and phase_actors.initial[0] is CycleModel2

    assert len(phase_actors.consumes) == 2
    assert CycleModel1 in phase_actors.consumes
    assert CycleModel2 in phase_actors.consumes

    assert len(phase_actors.produces) == 1
    assert CycleModel1 in phase_actors.produces


def test_actor_phases_order():
    initial_actors = (CycleActor3, CycleActor2)
    phase_actors = PhaseActors(initial_actors)

    assert len(phase_actors.actors) == 2
    assert phase_actors.actors[0] is CycleActor2
    assert phase_actors.actors[1] is CycleActor3

