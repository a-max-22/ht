# core/homotopy_groups.py

class HomotopyGroup(Generic[T]):
  ...
  def __iter__(self):
      '''
      Simple iterator that goes through added elements in the group.
      Another possible option - to make iterator that generates all possible 
      elements through group's generating set.  But to make this option we have to know whether 
      the group operation is commutative or not, and some other things
      '''
      yield from self.elements


    def find_inverse(self, index: int) -> int:
        if index not in self.elements:
            raise ValueError("Invalid element indices")

        curr_elem = self.elements[index]

        identity = InfinityGroupoid.identity(curr_elem.start, curr_elem.dimension)

        for ind, elem in self.elements.items():
            if ind == index:
                continue
            try:
                composition = InfinityGroupoid.compose(curr_elem, elem)
            except ValueError:
                continue

            if InfinityGroupoid.is_homotopic_equivalent(composition, identity):
                return ind
             
        raise ValueError("Cannot find inverse element in group")



# core/test_homotopy_groups.py
def test_find_inverse() -> bool:
  # 10 Test find inverse
  group     = HomotopyGroup(base_point, 1)
  loop_a    = HigherPath.base_path(base_point, base_point)
  invers    = HigherPath.base_path(base_point, base_point)

  a_id = group.add_element(loop_a)
  inv_id = group.add_element(invers)

  identity = InfinityGroupoid.identity(loop_a.start, loop_a.dimension)
  comp_id = group.compose(a_id, inv_id)

  assert inv_id == group.find_inverse(a_id)
  assert InfinityGroupoid.is_homotopic_equivalent(identity, group.elements[comp_id])

