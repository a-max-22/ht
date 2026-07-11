import blessed
import time
import random
from typing import Tuple, Optional, Callable

# Импорт модулей HoTT
from core.base_types import Product, Sum, Unit, unit
from core.path import Path
from core.torus import NTorus
from core.dependent_types import Pi

# Импорт компонентов игры
from game_field import GameField
from snake import Snake
from game_data_structures import Direction, GameEvent, GameState
from input_handler import InputHandler
from game_engine import GameEngine
from renderer import Renderer
from demo_mode import demo_strategy

def initialize_game(
    width: int, 
    height: int
) -> Tuple[GameField, GameState]:
    """
    Инициализирует игру с полем и начальным состоянием.
    
    Args:
        width: Ширина игрового поля
        height: Высота игрового поля
        
    Returns:
        Кортеж (игровое_поле, начальное_состояние)
    """
    # Создаем игровое поле
    game_field = GameField(width, height)
    
    # Начальная позиция змейки (центр поля)
    start_x, start_y = width // 2, height // 2
    initial_position = game_field.create_position(
        start_x, start_y
    )
    
    # Создаем змейку
    snake = Snake(initial_position)
    
    # Начальная позиция еды (случайная)
    food_x = random.randint(0, width - 1)
    food_y = random.randint(0, height - 1)
    food_position = game_field.create_position(
        food_x, food_y
    )
    
    # Начальное состояние игры с флагами паузы и выхода
    initial_state = GameState(snake, food_position)
    
    return game_field, initial_state


def handle_key_press(current_state:GameState, input_handler:InputHandler,
                     key):
    # Преобразование клавиши в строку
    key_name = key.name or key
    print(f"Нажата клавиша: {key_name}")
                
    # Обработка ввода и получение состояния
    new_state = input_handler.handle_input(key_name,
                                           current_state)
    print(f"Направление после ввода: \
          {Direction.to_string(new_state.get_snake().direction)}")
    
    return new_state


def process_user_input(state:GameState, 
                       input_handler:InputHandler,
                       term):
    # Проверка ввода (неблокирующая)
    key = term.inkey(timeout=0.01)
            
    # Обработка ввода при нажатии
    if key:
        return handle_key_press(state, input_handler, key)
        

def update_game_state(game_engine:GameEngine):        
    new_state = game_engine.update()
    if new_state:
        game_engine.set_state(new_state)


def run_game(game_engine:GameEngine, renderer:Renderer,
             frame_delay:float, game_mode:Pi, is_demo = False):
    
    last_update_time = time.time()
    
    state_change_strategy = game_mode(is_demo)

    # Цикл до установки флага выхода
    while not game_engine.get_current_state().is_quit_requested():
        # Обновить состояние игры, согласно ее режиму
        # Для этого используем пи-тип, который определяет 
        # стратегию изменения состояния игры
        cur_state = game_engine.get_current_state()
        new_state = state_change_strategy(cur_state)
        if new_state:
            game_engine.set_state(new_state)

        # Периодическое обновление состояния
        current_time = time.time()
        if current_time - last_update_time >= frame_delay:            
            update_game_state(game_engine)
            
            # Отрисовка текущего состояния
            renderer.render(
                    game_engine.get_current_state(),
                    game_engine.get_current_state()\
                        .is_game_over(),
                    game_engine.get_current_state()\
                        .is_paused()
                )
                
            last_update_time = current_time
            
        # Замедление цикла при завершении игры
        if game_engine.get_current_state()\
               .is_game_over() and \
               not game_engine.get_current_state()\
               .is_quit_requested():
                time.sleep(0.1)


def main():
    # Инициализация терминала blessed
    term = blessed.Terminal()
    
    # Конфигурация игры
    width, height = 20, 15
    frame_delay = 0.1  # Задержка между кадрами
    is_demo = True 

    # Инициализация компонентов игры
    game_field, initial_state = initialize_game(
        width, height
    )
    game_engine = GameEngine(
        game_field, initial_state
    )

    input_handler = InputHandler(initial_state)
    renderer = Renderer(term, game_field)

    game_mode = Pi(
            domain = GameState,
            codomain =lambda _: Callable,
            function = lambda t: {
                False: lambda x: \
                    process_user_input(x,
                                       input_handler,
                                       term),
                True: lambda x:demo_strategy(x, game_field),
            }.get(t, lambda x: x))


    snake = game_engine.current_state.get_snake()
    assert snake.contains_position(game_field.create_position(
        snake.body[0].first_value,
        snake.body[0].second_value,

        ))

    # Главный игровой цикл
    with term.cbreak(), term.hidden_cursor(), term.fullscreen():
        run_game(game_engine, renderer,
                 frame_delay, game_mode, 
                 is_demo)
        

if __name__ == "__main__":
    main()
