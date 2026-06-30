from core.dependent_types import Pi, Sigma
from core.base_types import Empty
from typing import Any, Callable


def test_dependent_types_extra() -> bool:
    # Расширил тест валидацией условия отсортированности массива
    def is_sorted(lst):
        return all(lst[i] <= lst[i+1] for i in range(len(lst)-1))
            
    try:
        sorted_container = Sigma(
                domain=list,
                codomain=lambda lst: bool if is_sorted(lst) else Empty,
                first=[1, 2, 3, 4],
                second=True
            )
            
        invalid_container = Sigma(
                domain=list,
                codomain=lambda lst: bool if is_sorted(lst) else Empty,
                first=[3, 1, 4, 2],
                second=True
            )
            
        assert False, "Failed to detect invalid Sigma value"
    except TypeError as e:
        pass

    # дополнительный тест сигма-типа: непустой список
    try:
        non_empty_container = Sigma(
                domain=list,
                codomain=lambda lst: bool if len(lst) > 0 else Empty,
                first=[1, 2, 3, 4],
                second=True
            )
            
        invalid_container = Sigma(
                domain=list,
                codomain=lambda lst: bool if len(lst) > 0 else Empty,
                first=[],
                second=True
            )
            
        assert False, "Failed to detect invalid Sigma value"
    except TypeError as e:
        pass

 

if __name__ == "__main__":
    test_dependent_types_extra()
