# вновь добавленные методы для реализации pentagon_identity 
# также метод higher_compose
class InfinityGroupoid(Generic[T]):
    @staticmethod
    def whiskering_right(p: HigherPath[T], q: HigherPath[T]) -> HigherPath[T]:
        """Vertical composition of paths with different dimensions"""
        if p.dimension <= q.dimension:
            raise ValueError("Second path must have lower dimension")
            
        return HigherPath(
            p.dimension,
            p.start,
            q.end,
            p.previous_paths + [q],
            None
        )

    @staticmethod
    def vertical_compose(p: HigherPath[T], q: HigherPath[T]) -> HigherPath[T]:
        """
            Simplfied method of vertical composition of higher paths without checking
            if the end of the first higher path equals the start of the second higher path
        """
        if p.dimension == 1:
            return InfinityGroupoid.compose(p, q)

        if p.dimension != q.dimension:
            raise ValueError("Paths have to be of equal dimensions")

        if p.start != q.start and p.end != q.end:
            raise ValueError("Paths are not vertically composable")

        # TODO: check if the end of the first path (lower dimension path)
        # is equivalent to the start of the second (lower dimension path)
        
        return HigherPath(
            p.dimension,
            p.start,
            p.end,
            [p.previous_paths[0], q.previous_paths[1]],
            None
        )

    @staticmethod
    def higher_compose(p: HigherPath[T], q: HigherPath[T]) -> HigherPath[T]:
        """Horizontal composition of higher paths"""
        if p.dimension != q.dimension:
            raise ValueError("Composed paths must have equal dimensions")

        if p.end != q.start:
            raise ValueError(f"The end of the first path ({p.end}) have to be the same as the start of the second path ({q.start})")

        if p.dimension == 1:
            return InfinityGroupoid.compose(p, q)


        if len(p.previous_paths) != len(q.previous_paths):
            raise ValueError("composed higher paths have to contain the same quantity of previous dimensions paths")

        compositions = [InfinityGroupoid.higher_compose(p_s, q_s) \
                        for p_s, q_s in zip(p.previous_paths, q.previous_paths)]
        

        return HigherPath(p.dimension, p.start, q.end, compositions)
