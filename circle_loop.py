

from path import Path
from base_types import unit

class LoopCount:
    def __init__(self, loop_count):
        self.loop_count = loop_count

class LoopPath(Path):
    def __init__(self, base_point, cycles_count = 0):
        super().__init__(base_point, base_point)
        self.cycles_count = cycles_count
    
    def trans(self, other):
        if not isinstance(other, LoopPath):
            return super().trans(other)
        if self.start != other.start:
            raise ValueError("Cannot compose loop paths: base points have to be equal")

        result = LoopPath(self.start, self.cycles_count + other.cycles_count)
        result._trans_components = [self, other]
        return result

    def sym(self):
        return LoopPath(self.start, -self.cycles_count)


class CircleLoop(LoopPath):
    def __init__(self, base_point = unit, cycles_count = 0):
        super().__init__(base_point, cycles_count)

    def compose(self, other):
        if not isinstance(other, CircleLoop):
            return super().trans(other)
        if self.start != other.start:
            raise ValueError("Cannot compose circle loops with different base points")
        return CircleLoop(self.start, self.cycles_count + other.cycles_count)
    
    def inv(self):
        return super().sym()
    
    def neutral_elem(self):
        return CircleLoop(self.start)
