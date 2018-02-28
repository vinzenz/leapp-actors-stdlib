import sys

from leapp.utils.meta import with_metaclass
from workflows.phases import Phase
from workflows.phaseactors import PhaseActors


def _phase_sorter_key(a):
    return a.get_index()


def _is_phase(attr):
    return isinstance(attr, type) and issubclass(attr, Phase)


def _get_phases_sorted(attrs):
    return tuple(sorted([attr for attr in attrs.values() if _is_phase(attr)], key=_phase_sorter_key))


class WorkflowMeta(type):
    def __new__(mcs, name, bases, attrs):
        klass = super(WorkflowMeta, mcs).__new__(mcs, name, bases, attrs)
        if not getattr(sys.modules[mcs.__module__], name, None):
            setattr(sys.modules[mcs.__module__], name, klass)
        klass.phases = _get_phases_sorted(attrs)
        return klass


class Workflow(with_metaclass(WorkflowMeta)):
    def __init__(self):
        self._all_consumed = set()
        self._all_produced = set()
        self._initial = set()
        self._phase_actors = []

        for phase in self.phases:
            self._apply_phase(phase.filter.get_pre())
            self._apply_phase(phase.filter.get())
            self._apply_phase(phase.filter.get_post())

    def _apply_phase(self, actors):
        self._phase_actors.append(PhaseActors(actors))
        self._initial.update(set(self._phase_actors[-1].initial) - self._all_produced)
        self._all_consumed.update(self._phase_actors[-1].consumes)
        self._all_produced.update(self._phase_actors[-1].produces)

    @property
    def initial(self):
        return self._initial

    @property
    def consumes(self):
        return self._all_consumed

    @property
    def produces(self):
        return self._all_produced

    def run(self, *args, **kwargs):
        pass
