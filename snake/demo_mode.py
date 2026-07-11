from core.path import Path
from core.base_types import Product

from game_data_structures import Direction, GameEvent, GameState
from game_field import GameField
from snake import Snake
from typing import List, Tuple, TypeAlias, Any, Callable, Iterable, Dict
from collections import deque

Node:TypeAlias = Any 
EnumNeighborsFunc: TypeAlias = Callable[[Node], Iterable[Node]]


def find_shortest_path_bfs(start: Node, target: Node,
                           get_neighbors: EnumNeighborsFunc) -> List[Node]:
    if start == target:
        return [start]

    queue: deque[Node] = deque([start])
    parents: dict[Node, Node] = {start: start}

    while queue:
        current = queue.popleft()

        if current == target:
            path = []
            while current != start:
                path.append(current)
                current = parents[current]
            path.append(start)
            return path[::-1]

        for neighbor in get_neighbors(current):
            if neighbor not in parents:
                parents[neighbor] = current
                queue.append(neighbor)
    return [] 


def field_get_free_cell_neighbors(state:GameState,
                                  field:GameField,
                                  cell:Product) -> List[Product]:
    snake = state.get_snake()
    x, y = cell.first_value, cell.second_value

    neighbors_possible = map(lambda args: field.create_position(*args),
                             [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
    free_neighbors = []

    for neighbor in neighbors_possible:
        if snake.contains_position(neighbor):
            continue
        
        free_neighbors.append(neighbor)

    return free_neighbors

# MotionVector is Product[Path, Direction]
MotionVector:TypeAlias = Product 
Way:TypeAlias = List[MotionVector]

def get_direction_for_neighbor_points(field:GameField,
                                      start:Product,
                                      end:Product) -> Direction | None:
    width, height = field.get_dimensions()
    dx = (end.first_value - start.first_value + width // 2 ) % width - width // 2  
    dy = (end.second_value - start.second_value + height // 2) % height - height // 2

    if dx < 0 and dy == 0:
        return Direction.left()
    if dx > 0 and dy == 0:
        return Direction.right()
    if dy < 0 and dx == 0:
        return Direction.up()
    if dy > 0 and dx == 0:
        return Direction.down()
    
    return None

'''
Простая стратегия, которая ищет самый простой путь до еды, 
не учитывая возможность столкновения  с собой
'''
def find_dumb_way_to_reach_the_food(state:GameState) -> Way:
    food_position = state.get_food_position()
    head_position = state.get_snake().get_head()
    dx = food_position.first_value - head_position.first_value  
    dy = food_position.second_value - head_position.second_value  

    path_horizontal_end = Product(head_position.first_value + dx, head_position.second_value)
    path_horizontal = Path(head_position, path_horizontal_end)
    path_vertical = Path(path_horizontal_end, food_position)
    return [ Product.from_tuple(( path_horizontal, Direction.left() if dx < 0 else Direction.right()) ), 
            Product.from_tuple(( path_vertical, Direction.up() if dy < 0 else Direction.down() ))]


'''
Стратегия, которая ищет кратчайший возможный путь до еды. 
Стратегия не учитывает возможность того, что змея окажется в тупике
после того, как съест еду.
'''
def find_shortest_way_to_food(state:GameState, field:GameField) -> Way:
    food_position = state.get_food_position()
    head_position = state.get_snake().get_head()
    
    get_neighbors = lambda x: field_get_free_cell_neighbors(state, field, x)
    path = find_shortest_path_bfs(head_position, food_position, get_neighbors)
    
    if len(path) <= 1:
        return []
    
    way = []
    cur = path[0]
    direction = get_direction_for_neighbor_points(field, cur, path[1])
    start_path = cur

    for next_point in path[1:]:
        new_direction = get_direction_for_neighbor_points(field, cur, next_point)
        
        if (new_direction is not None and \
            new_direction != direction):
            
            motion_vector = (Path(start_path, cur), direction)
            way.append(Product.from_tuple(motion_vector))

            start_path = cur
            direction = new_direction
        
        cur = next_point
    
    motion_vector = (Path(start_path, next_point), direction)
    way.append(Product.from_tuple(motion_vector))
    print("\n\nНашел путь к еде, двигаюсь к ней!")


    return way


'''
Следуем найденному пути, меняя направление змейки при достижении заданной точки
'''
def follow_way(state:GameState, way:Way) -> Tuple[GameState, Way]:
    if not way:
        return state, way

    snake = state.get_snake() 
    head = snake.get_head()
    
    current_path, current_direction = way[0].to_tuple()

    at_the_start_of_the_path = (head == current_path.start) 

    if at_the_start_of_the_path:
        new_snake = snake.set_direction(current_direction)
        state = state.with_new_snake(new_snake)

    end_of_path_reached = (head == current_path.end) 

    if not end_of_path_reached:
        return state, way

    end_of_way_reached = not way[1:]    
    if end_of_way_reached:
        return state, []

    new_path, new_direction = way[1].to_tuple()
    new_snake = snake.set_direction(new_direction)
    return state.with_new_snake(new_snake), way[1:]

'''
Обновляем вспомогательную структуру, где хранятся сведения
о произведенных нами расчетах путей
'''
def update_strategy_state(state:GameState, 
                          field: GameField,
                          strategy_state:Dict) -> Dict:
    strategy_state['food_position'] = state.get_food_position() 
    strategy_state['way_to_food'] = find_shortest_way_to_food(state, 
                                                              field)    
    return strategy_state


def is_food_already_consumed(state:GameState,
                             prev_food_position:Product) -> bool:
    return prev_food_position != state.get_food_position() 

'''
Стратегия, которая применяется, когда невозможно найти путь до еды на данном шаге. 
В этом случае мы просто случайно переходим в любою свободную клетку. 
'''
def avoid_collisions(state:GameState, field:GameField) -> GameState:
    snake:Snake = state.get_snake()
    head = snake.get_head()

    _, new_snake = snake.move(field)        
    collision_event = new_snake.check_self_collision()     
    is_collision_on_next_move = GameEvent.is_collision(collision_event)   

    if not is_collision_on_next_move:
        return state
    
    print('\n\nПуть к еде заблокирован, двигаюсь чтобы не столкнуться с собой')
    
    from random import choice 
    free_neighbors = field_get_free_cell_neighbors(state, field, head)
    
    # нет никаких вариантов избежать столконовения
    # змейка в тупике
    if not free_neighbors:
        print('\n\nНе вижу вариантов избежать столкновения =( \n Пока-пока!')    
        return state
    next_cell = choice(free_neighbors)
    new_direction = get_direction_for_neighbor_points(field,
                                                      head,
                                                      next_cell)
    
    assert new_direction is not None
    
    new_snake = snake.set_direction(new_direction)
    return  state.with_new_snake(new_snake)


'''
Реализуем демо-режим игры в змейку. Выбираем кратчайший путь до цели 
с учетом препятствий, но без учета того, что змейка может оказаться в тупике. 
Если не можем достичь еды, просто уходим от столкновения, пока путь не окажется открытым.
'''
def demo_strategy(state:GameState,
                  field:GameField,
                  strategy_state = {}) -> GameState|None:
    if not strategy_state:
        strategy_state = update_strategy_state(state, 
                                               field,
                                               strategy_state)
        return None
    

    if is_food_already_consumed(state, strategy_state['food_position']) or \
        not strategy_state['way_to_food']:
        strategy_state = update_strategy_state(state, 
                                               field,
                                               strategy_state) 
    
    way_to_food = strategy_state['way_to_food']

    if not way_to_food:
        return avoid_collisions(state, field)

    state_or_none, way_remained = follow_way(state, way_to_food)
    strategy_state['way_to_food'] = way_remained
    
    return state_or_none
