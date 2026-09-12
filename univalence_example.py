
from dataclasses import dataclass
import copy

from core.univalence import create_type_equivalence, Univalence, Equivalence

class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()

    def len(self):
        return len(self._items)

    def to_list(self):
        return self._items.copy()


def stack_to_list(s:Stack):
    return s.to_list()


def list_to_stack(l:list):
    s = Stack()
    for elem in l: s.push(elem)
    return s


def are_stacks_equal(s1: Stack, s2: Stack):
    s1_copy = copy.deepcopy(s1)
    s2_copy = copy.deepcopy(s2)

    try:
        while True:
            elem1 = s1_copy.pop()
            elem2 = s2_copy.pop()

            if elem1 != elem2:
                return False

    except IndexError:
        return s1_copy.len() == 0  and s2_copy.len() == 0 


def are_lists_equal(l1, l2):
    if not l1 and not l2:
        return True
    if not l1 or not l2:
        return False
    
    return l1[0] == l2[0] and are_lists_equal(l1[1:], l2[1:])


def test_stack_list_equivalence():
    equivalence = create_type_equivalence(Stack, list, 
                                          stack_to_list, list_to_stack)

    # тестирование равенества исходного и восстановленного стека
    stack = Stack()
    lst = ['a', 'b', 'c']
    for i in lst:
        stack.push(i)

    lst_conv = equivalence.function(stack)
    restored = equivalence.inverse.backward(lst_conv)

    assert are_stacks_equal(stack, restored)

    # тестирование сохранения порядка элементов при конвертации в список
    s_copy = copy.deepcopy(stack)
    for elem in reversed(lst):
        assert s_copy.pop() == elem

    # тестирование преобразования пустых стеков
    stack_empty = Stack()
    lst_empty = []

    assert are_lists_equal(equivalence.function(stack_empty), lst_empty)
    assert are_stacks_equal(equivalence.inverse.backward(lst_empty), stack_empty)

@dataclass
class Celsius:
    t: int

@dataclass
class Farenheit:
    t: int

def celsius_to_farenheit(c:Celsius) -> Farenheit:
    return Farenheit( int (c.t * (9 / 5) + 32 ))


def farenheit_to_celsius(f:Farenheit) -> Celsius:
    return Celsius( int( (f.t - 32) * (5 / 9)))

def test_temperatures_equivalence():
    c_t_equiv = create_type_equivalence(Celsius, Farenheit, 
                                        celsius_to_farenheit,
                                        farenheit_to_celsius)

    t_c_equiv = create_type_equivalence(Farenheit, Celsius, 
                                        farenheit_to_celsius,
                                        celsius_to_farenheit)

    # тестирование коммутативности преобразования 
    temp_cel = Celsius(30)
    temp_far = Univalence.transport_uni_axi(Celsius, Farenheit,
                                        c_t_equiv, temp_cel)

    assert c_t_equiv.inverse.backward(temp_far) == temp_cel
    assert Univalence.transport_uni_axi(Farenheit, Celsius,
                                        t_c_equiv, temp_far) == temp_cel


    # проверка корректности конвертации на примере хорошо известных значений
    assert Univalence.transport_uni_axi(Celsius, Farenheit,
                                        c_t_equiv, Celsius(0)) == Farenheit(32) 

    assert Univalence.transport_uni_axi(Celsius, Farenheit,
                                        c_t_equiv, Celsius(100)) == Farenheit(212) 


import json
import xml.etree.ElementTree as ElemTree

class JSONData:
    def __init__(self, data: str):  # JSON строка
        self.data = json.loads(data)

class XMLData:
    def __init__(self, data: str):  # XML строка
        self.root = ElemTree.fromstring(data)

class PythonDict:
    def __init__(self, data: dict):  # Python словарь
        self.data = data


def json_to_dict(j: JSONData) -> PythonDict:
    return PythonDict(j.data.copy())


def dict_to_json(d: PythonDict) -> JSONData:
    return JSONData(json.dumps(d))


def dict_to_xml(d: PythonDict) -> XMLData:
    root = ElemTree.Element("root")

    for key, value in d.data.items():
        child = ElemTree.SubElement(root, key)
        child.text = str(value)

    xml_bytes = ElemTree.tostring(root, encoding="utf-8")

    return XMLData(xml_bytes)


def xml_to_dict(x: XMLData) -> PythonDict:
    result_dict = {}

    for child in x.root:
        val = child.text
        if val.isdigit():
            val = int(val)
        else:
            try: val = float(val)
            except ValueError: pass
        
        result_dict[child.tag] = val

    return PythonDict(result_dict)



def test_equiv_composition():
    json_dict_equiv = create_type_equivalence(JSONData, PythonDict, 
                                        json_to_dict,
                                        dict_to_json)

    dict_xml_equiv = create_type_equivalence(PythonDict, XMLData, 
                                        dict_to_xml,
                                        xml_to_dict)

    json_xml_equiv = Equivalence.compose(json_dict_equiv, dict_xml_equiv)

    # эквивалентность преобразований разными путями
    json_str = '{"name":"John", "age":30}'
    json_data = JSONData(json_str)
    xml_via_compose = Univalence.transport_uni_axi(JSONData, XMLData,
                                                  json_xml_equiv, json_data)

    dct = Univalence.transport_uni_axi(JSONData, PythonDict,
                                                  json_dict_equiv, json_data)

    xml_via_sequence = Univalence.transport_uni_axi(PythonDict, XMLData,
                                                  dict_xml_equiv, dct)

    r1 = ElemTree.tostring(xml_via_compose.root, encoding="utf-8").decode("utf-8")
    r2 = ElemTree.tostring(xml_via_sequence.root, encoding="utf-8").decode("utf-8")

    assert r1 == r2

    # композиция путей соответствует композиции эквивалентностей
    json_dct_path = Univalence.uni_axi(JSONData, PythonDict,
                                        json_dict_equiv)

    dict_xml_path = Univalence.uni_axi(PythonDict, XMLData,
                                       dict_xml_equiv)
    
    paths_composition = json_dct_path.trans(dict_xml_path)

    equiv_composition_path = Univalence.uni_axi(JSONData, XMLData,
                                                      json_xml_equiv)

    assert paths_composition == equiv_composition_path

 
if __name__ == "__main__":
    test_stack_list_equivalence()
    test_temperatures_equivalence()
    test_equiv_composition()
