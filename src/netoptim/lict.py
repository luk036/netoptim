from typing import MutableMapping
from typing import Iterator, TypeVar, List

T = TypeVar("T")


class Lict(MutableMapping[int, T]):
    def __init__(self, lst: List[T]) -> None:
        """Dict-like adaptor for a list

        Args:
            lst (list): _description_
        """
        self.rng = range(len(lst))
        self.lst = lst

    def __getitem__(self, key: int) -> T:
        """_summary_

        Args:
            key (_type_): _description_

        Returns:
            _type_: _description_

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> a[2]
            3
        """
        return self.lst.__getitem__(key)

    def __setitem__(self, key: int, new_value: T):
        """_summary_

        Args:
            key (_type_): _description_
            new_value (_type_): _description_

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> a[2] = 7
            >>> print(a[2])
            7
        """
        self.lst.__setitem__(key, new_value)

    def __delitem__(self, _):
        """(You really should not delete item from Lict)

        Args:
            key (_type_): _description_

        Returns:
            _type_: _description_
        """
        raise NotImplementedError()

    def __iter__(self) -> Iterator:
        """_summary_

        Returns:
            _type_: _description_

        Yields:
            Iterator: _description_

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> for i in a:
            ...     print(i)
            0
            1
            2
            3
        """
        return iter(self.rng)

    def __contains__(self, value) -> bool:
        """_summary_

        Args:
            value (_type_): _description_

        Returns:
            bool: _description_

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> 2 in a
            True
        """
        return value in self.rng

    def __len__(self) -> int:
        """_summary_

        Returns:
            _type_: _description_

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> len(a)
            4
        """
        return len(self.rng)

    def values(self):
        """_summary_

        Returns:
            _type_: _description_

        Yields:
            Iterator: _description_

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> for i in a.values():
            ...     print(i)
            1
            4
            3
            6
        """
        return iter(self.lst)

    def items(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return enumerate(self.lst)

    # def copy(self):
    #     return Lict(self.lst.copy())


if __name__ == "__main__":
    a = Lict([0] * 8)
    for i in a:
        a[i] = i * i
    for i, vtx in a.items():
        print(f"{i}: {vtx}")
    print(3 in a)
