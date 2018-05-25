import collections
import typing

T = typing.TypeVar('T')


class ChainableIterator(typing.Iterator[T], collections.Iterator):
    def __init__(self, *iterators: typing.Iterator[T]):
        self._index = -1
        self._iterators = list((a for a in b) for b in iterators)

    def __next__(self):
        try:
            if self._index < 0:
                raise StopIteration
            return next(self._iterators[self._index])
        except StopIteration as e:
            if self._index < len(self._iterators) - 1:
                self._index += 1
                return next(self)
            raise e

    def chain(self, *iterators: typing.Iterator[T]) -> 'ChainableIterator[T]':
        self._iterators.extend((a for a in b) for b in iterators)
        return self
