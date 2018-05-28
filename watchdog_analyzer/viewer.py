import abc
import curses
import typing

from npyscreen import ActionFormMinimal, Form, MLTreeAction, MultiLineAction, NPSAppManaged, TreeData

from watchdog_analyzer import analyzer
from watchdog_analyzer.chainable_iterator import ChainableIterator
from watchdog_analyzer.trace import Trace

_MAIN_FORM = '_MAIN_FORM'
_MEMORY_USAGE_FORM = '_MEMORY_USAGE_FORM'
_MEMORY_LEAKS_FORM = '_MEMORY_LEAKS_FORM'


def _keys():
    for i in ('<', '>', '[', ']', '.', ',', '-'):
        yield ord(i)
    yield from range(ord('a'), ord('z') + 1)
    yield from range(ord('A'), ord('Z') + 1)


class _AnalysisSelectorWidget(MultiLineAction):
    _OPTIONS = ('Memory Usage', 'Memory Leaks',)
    _FORMS = (_MEMORY_USAGE_FORM, _MEMORY_LEAKS_FORM)

    def __init__(self, *args, **kwargs):
        super(_AnalysisSelectorWidget, self).__init__(*args, **kwargs)
        for k in _keys():
            self.handlers.pop(k, None)
        self.handlers[ord('q')] = self.h_exit
        self.values = self._OPTIONS

    def actionHighlighted(self, _act_on_this, _key_press):
        self.parent.parentApp.switchForm(self._FORMS[self.cursor_line])


class _AnalysisSelectionForm(ActionFormMinimal):
    def create(self):
        self.name = 'Watchdog Analyzer'
        self.add(_AnalysisSelectorWidget)

    def on_ok(self):
        self.parentApp.setNextForm(None)


class _TreeWidget(MLTreeAction):
    def __init__(self, *args, **kwargs):
        super(_TreeWidget, self).__init__(*args, **kwargs)
        for k in _keys():
            self.handlers.pop(k, None)
        self.handlers.update({
            curses.KEY_RIGHT: self.h_expand_tree,
            curses.KEY_LEFT: self.h_collapse_tree,
            ord('{'): self.h_expand_all,
            ord('}'): self.h_collapse_all,
            ord('q'): self.h_exit,
        })
        self.slow_scroll = True

    def actionHighlighted(self, act_on_this: TreeData, key_press):
        if act_on_this.expanded:
            self.h_collapse_tree(key_press)
        else:
            self.h_expand_tree(key_press)


class _TreeForm(Form, metaclass=abc.ABCMeta):
    _trace: typing.Optional[Trace] = None

    @classmethod
    def inject_trace(cls, trace: Trace) -> typing.Type['_TreeForm']:
        if cls._trace:
            raise ValueError
        cls._trace = trace
        return cls

    def get_trace(self) -> Trace:
        if not self._trace:
            raise ValueError
        return self._trace

    def afterEditing(self):
        self.parentApp.switchFormPrevious()

    @staticmethod
    def _create_values(objects: typing.Mapping) -> TreeData:
        root = TreeData()
        iterator = ChainableIterator(((root, objects),))
        for node, data in iterator:
            for key, value in data.items():
                if isinstance(value, dict):
                    iterator.chain(((node.new_child(content=f'{key}', expanded=False), value),))
                elif isinstance(value, list):
                    iterator.chain(((node.new_child(content=f'{key}', expanded=False), dict(enumerate(value))),))
                else:
                    node.new_child(content=f'{key}: {value}', expanded=False)
        return root


class _MemoryUsageForm(_TreeForm):
    def create(self):
        self.name = 'Watchdog Analyzer [Memory Usage]'
        self.add(_TreeWidget, values=self._create_values(analyzer.get_all(self.get_trace())))


class _MemoryLeaksForm(_TreeForm):
    def create(self):
        self.name = 'Watchdog Analyzer [Memory Leaks]'
        self.add(_TreeWidget, values=self._create_values(analyzer.get_leaks(self.get_trace())))


class Viewer(NPSAppManaged):
    _trace: typing.Optional[Trace] = None

    STARTING_FORM = _MAIN_FORM

    @classmethod
    def inject_trace(cls, trace: Trace) -> typing.Type['Viewer']:
        if cls._trace:
            raise ValueError
        cls._trace = trace
        return cls

    @classmethod
    def build(cls) -> 'Viewer':
        return cls()

    def get_trace(self) -> Trace:
        if not self._trace:
            raise ValueError
        return self._trace

    def onStart(self):
        self.addForm(_MAIN_FORM, _AnalysisSelectionForm)
        self.addForm(_MEMORY_USAGE_FORM, _MemoryUsageForm.inject_trace(self.get_trace()))
        self.addForm(_MEMORY_LEAKS_FORM, _MemoryLeaksForm.inject_trace(self.get_trace()))
