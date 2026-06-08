from core.base_types import Sum, Product
from typing import List, Any

'''
sum - type
Статус вычисления? Либо ошибка, либо удавшаяся часть 
Но это как будто бы не полностью подходит и больше про монаду наверное
Что еще? 

Либо пустая нода, либо нормальная 
Узел в дереве. 
'''
from enum import Enum

class Op(Enum):
    ADD = 1
    SUBSTRACT = 2
    MULIPLY = 3
    DIVIDE = 4

class Operation:
    def __init__(self, op:Op, args:List[Any]):
        self.args = args
        self.op = op

class Num:
    def __init__(self, val:int|float):
        self.value = val
    
    def __str__(self):
        return str(self.val)

# специальекласс для операции, которая пока не 
class Undefined:
    def __init__(self):
        pass


def test_types():
    # простой пример узла в AST-дереве,
    # который может быть как в статусе Undefined, 
    # т.е. как узел, который еще по какой-то причине не разобран
    # так и быть обычным, "полноценным"
    expr = Sum(Operation(Op.ADD, [Num(1), Num(2)]), Undefined)

    # пример результата выполнения функции, который может быть, к примеру числовым, либо 
    # неопределенным, если произошла ошибка
    calc_result = Sum(1, None)


    # любую операцию из AST  выше можно представить как Product-тип, 
    # объединяющий операцию и аргументы
    op = Product(Op.ADD, [Num(1), Num(2)])

    # еще один пример: сведения о функции в исполняемом файле можно представить как Product-тип
    address = 0x4040
    name = 'init'
    func_info = Product(address, name)


if __name__ == "__main__":
    test_types()
