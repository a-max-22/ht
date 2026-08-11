# core/infinity_groupoid.py
    def does_higher_path_exist(p: HigherPath[T], q: HigherPath[T]) -> HigherPath[T]:
        '''
        Placeholder for method to check if there exists hogher path between two paths
        Now we don't have any mandatory HomSpace that by default owns each newly created path
        Two possible solutions:
            - specify HomSpace when making operations with paths - creating, composing, etc
            - make some "universal" static homespace that holds all the paths
        '''
        return True


    def is_homotopic_equivalent(p: HigherPath[T], q: HigherPath[T]) -> HigherPath[T]:
        if p.dimension != q.dimension:
            return False

        if p.start != q.start and p.end != q.end:
            return False

        return InfinityGroupoid.does_higher_path_exist(p,q)

