from core.infinity_groupoid import *

def pentagon_identity():
    # строим 3-путь от одного способа расстановки скобок к другому
    # само существование этого 3-пути показывает эквивалентность способов расстановки скобок
    # для реализации построения путей строго через операции InfinityGroupoid
    # для того, чтобы оставаться строго в пределах операций InfinityGroupoid, туда добавлены следующие методы: 
    # vertical_compose - вертикальная композиция высших путей одинаковой размерности
    # whiskering_left - левый whiskering, когда путь меньшей размерности композируется с путем высшей размерности (реализация уже была изначально)
    # whiskering_right - правый  whiskering, когда путь  высшей размерности композируется c путем меньшей размерности
    
    p = HigherPath(1, "A", "B", [])
    q = HigherPath(1, "B", "C", [])
    r = HigherPath(1, "C", "D", [])
    s = HigherPath(1, "D", "E", [])

    # строим путь a1_s : ((p * q) * r) * s --> (p * (q * r)) * s
    a1 = CoherenceConditions.associativity(p, q, r)
    a1_s = InfinityGroupoid.whiskering_right(a1, s)
    
    # строим путь a3:  (p * (q * r)) * s --> p * ( (q * r) * s)
    a3 = CoherenceConditions.associativity(p, InfinityGroupoid.compose(q, r), s)
    
    # строим путь a2:  ((p * q) * r) * s --> (p * q) * (r * s_
    a2 = CoherenceConditions.associativity(p, InfinityGroupoid.compose(q, r), s)
    # строим путь p_a2:  p * ((q * r) * s) --> p * (q * (r * s))
    p_a2 = InfinityGroupoid.whiskering_left(p, a2)



    # строим путь a5: ((p * q) * r) * s -->  (p * q) * (r * s)
    a5 = CoherenceConditions.associativity(InfinityGroupoid.compose(p, q), r, s)
    
    # строим путь a4: (p * q) * (r * s) -->   p * (q * (r * s))
    a4 = CoherenceConditions.associativity(p, q, InfinityGroupoid.compose(r, s))

    # комбинируем "правый" и "левый" пути через вертикальную композицию
    path_start = InfinityGroupoid.vertical_compose(InfinityGroupoid.vertical_compose(a1_s, a3), p_a2)
    path_end = InfinityGroupoid.vertical_compose(a5, a4) 
    
    # строим итоговый 3-путь  между "правым" и "левым" путем 
    return HigherPath(3, path_start.start, path_start.end, [path_start, path_end]) 


pentagon_identity()
