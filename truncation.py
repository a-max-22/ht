class SetTruncation(Truncated[T]):
  ...
    @staticmethod
    def create_quotient_set(elements: List[T], \
                            relation: Callable[[T, T], bool]) -> Dict[T, List[T]]:
        quotient_set:Dict[T, List[T]] = {}
        for e in elements: 
            key = next((q for q in quotient_set if relation(e, q)), None)
            if key:
                quotient_set[key].append(e)
            else:
                quotient_set[e] = [e]

        return quotient_set
         

    @staticmethod
    def verify_equivalence_relation(relation: Callable[[T, T], bool],\
                                    elements: List[T]) -> bool:

        is_symmetric_and_reflexive = all(( relation(e2, e1) \
                                           for e1 in elements for e2 in elements \
                                           if relation(e1, e2) ))
        if not is_symmetric_and_reflexive: return False

        is_transitive = all(relation(e1, e3) \
                            for e1 in elements \
                            for e2 in elements \
                            for e3 in elements \
                            if relation(e1,e2) and relation(e2,e3)
        )

        return is_transitive
            
    @staticmethod
    def find_representative(element: T, quotient_classes: Dict[T, List[T]]) -> T:
        for k in quotient_classes:
            el = next((q for q in quotient_classes[k] if q == element), None)
            if el is not None:
                return k
        return None 
