from core.truncation import SetTruncation, TruncationLevel

def non_less_than(x:int, y:int):
    return x >= y

def modulus(x:int, y:int, mod: int):
    return (x  % mod) == (y % mod)

def non_transitive_reflexive_symmetric(x:int, y:int):
    return abs(x-y) <= 2

def test_set_truncation():
    # Ожидаемый результат:
    st = SetTruncation({1,2,3,4})

    # проверяем рефлексивное, транзитивное не симметриченое отношение
    assert not st.verify_equivalence_relation(non_less_than, st.value) 

    # проверяем рефлексивное, транзитивное, симметриченое отношение
    assert st.verify_equivalence_relation(lambda x,y: modulus(x, y, 2), st.value)

    # проверяем рефлексивное, симметриченое, не транзитивное отношение
    assert not st.verify_equivalence_relation(non_transitive_reflexive_symmetric, st.value)  

    is_odd = lambda x,y: modulus(x, y, 2)
    quot_set = st.create_quotient_set(st.value, is_odd)
    assert len(quot_set) == 2
    print(quot_set)

    rep = st.find_representative(3, quot_set)
    assert rep == 1



if __name__ == "__main__":
    test_set_truncation()
