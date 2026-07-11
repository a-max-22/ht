from typing import Optional, Any, Dict, Tuple
from core.base_types import Product, Sum, Unit, unit
from core.path import Path

class GameEvent:
    """
    Представляет игровые события с использованием 
    типа Sum из HoTT. 
    События могут быть: продолжение игры, 
    сбор еды, обнаружение столкновения.
    """
    
    @staticmethod
    def continue_game() -> Sum:
        """Игра продолжается в штатном режиме"""
        return Sum.left(unit, "CONTINUE")
    
    @staticmethod
    def food_collected() -> Sum:
        """Змейка собрала еду"""
        return Sum.right("FOOD_COLLECTED", unit)
    
    @staticmethod
    def collision_detected() -> Sum:
        """
        Змейка столкнулась с собой или 
        границей поля
        """
        return Sum.right("COLLISION", unit)
    
    @staticmethod
    def is_continue(event: Sum) -> bool:
        """Проверка события 'продолжение игры'"""
        return event.is_left_active
    
    @staticmethod
    def is_food_collected(event: Sum) -> bool:
        """Проверка события 'сбор еды'"""
        return not event.is_left_active and \
               event.right_value == "FOOD_COLLECTED"
    
    @staticmethod
    def is_collision(event: Sum) -> bool:
        """Проверка события 'столкновение'"""
        return not event.is_left_active and \
               event.right_value == "COLLISION"

class Direction:
    """
    Представляет направления движения с 
    использованием типа Sum из HoTT. 
    Каждое направление - вариант типа Sum с 
    соответствующими дельта-координатами.
    """
    
    @staticmethod
    def up() -> Sum:
        """Направление вверх (0, -1)"""
        return Sum.left((0, -1), "UP")
    
    @staticmethod
    def down() -> Sum:
        """Направление вниз (0, 1)"""
        return Sum.left((0, 1), "DOWN")
    
    @staticmethod
    def left() -> Sum:
        """Направление влево (-1, 0)"""
        return Sum.left((-1, 0), "LEFT")
    
    @staticmethod
    def right() -> Sum:
        """Направление вправо (1, 0)"""
        return Sum.left((1, 0), "RIGHT")
    
    @staticmethod
    def get_delta(direction: Sum) -> Tuple[int, int]:
        """
        Извлечение дельты движения из 
        направления Sum
        """
        return direction.match(
            lambda value: value,
            lambda _: (0, 0)  # Резервный вариант
        )
    
    @staticmethod
    def are_opposite(dir1: Sum, dir2: Sum) -> bool:
        """Проверка противоположных направлений"""
        delta1 = Direction.get_delta(dir1)
        delta2 = Direction.get_delta(dir2)
        
        return delta1[0] == -delta2[0] and delta1[1] == -delta2[1]
    
    @staticmethod
    def to_string(direction: Sum) -> str:
        """
        Получение строкового представления 
        направления
        """
        return direction.match(
            lambda _: direction.right_value,
            lambda _: "UNKNOWN"
        )

class GameState:
    """
    Представляет полное состояние игры с 
    использованием Product типов из HoTT. 
    Состояние игры объединяет состояние змейки, 
    позицию еды, счет и флаги управления игрой.
    """
    
    def __init__(self, snake, food_position: Product, 
                 score: int = 0, is_demo: bool = False):
        """
        Инициализация состояния игры: змейка, 
        позиция еды, счет и флаги управления.
        
        Аргументы:
            snake: Объект змейки
            food_position: Позиция еды как Product
            score: Текущий счет (по умолчанию: 0)
        """
        # Хранение змейки и еды вместе в Product
        self.entity_state = Product(snake, food_position)
        
        self.game_context_state  = Product(score, is_demo)
        
        # Хранение состояния и счета в Product
        self.state = Product(self.entity_state, self.game_context_state)
        
        # Флаги управления игрой
        self.paused = False
        self.game_over = False
        self.quit_requested = False
    
    def get_snake(self):
        """Получение змейки из состояния игры"""
        return self.entity_state.first_value
    
    def get_food_position(self) -> Product:
        """Получение позиции еды"""
        return self.entity_state.second_value
    
    def get_score(self) -> int:
        """Получение текущего счета"""
        return self.state.second_value.first_value
    
    def is_demo(self) -> bool: 
        """Проверка режима игры"""
        return self.state.second_value.second_value

    def is_paused(self) -> bool:
        """Проверка приостановки игры"""
        return self.paused
    
    def is_game_over(self) -> bool:
        """Проверка завершения игры"""
        return self.game_over
    
    def is_quit_requested(self) -> bool:
        """Проверка запроса выхода"""
        return self.quit_requested
    
    def with_new_snake(self, new_snake):
        """Создание состояния с обновленной змейкой"""
        new_state = GameState(new_snake, 
                              self.get_food_position(), 
                              self.get_score())
        new_state.paused = self.paused
        new_state.game_over = self.game_over
        new_state.quit_requested = self.quit_requested
        return new_state
    
    def with_new_food(self, new_food_position: Product):
        """
        Создание состояния с обновленной 
        позицией еды
        """
        new_state = GameState(self.get_snake(), 
                              new_food_position, 
                              self.get_score())
        new_state.paused = self.paused
        new_state.game_over = self.game_over
        new_state.quit_requested = self.quit_requested
        return new_state
    
    def with_incremented_score(self, points: int = 1):
        """Создание состояния с увеличенным счетом"""
        new_score = self.get_score() + points
        new_state = GameState(self.get_snake(), 
                              self.get_food_position(), 
                              new_score)
        new_state.paused = self.paused
        new_state.game_over = self.game_over
        new_state.quit_requested = self.quit_requested
        return new_state
    
    def with_toggled_pause(self):
        """
        Создание состояния с переключенным 
        флагом паузы
        """
        new_state = GameState(self.get_snake(), 
                              self.get_food_position(), 
                              self.get_score())
        new_state.paused = not self.paused
        new_state.game_over = self.game_over
        new_state.quit_requested = self.quit_requested
        return new_state
    
    def with_game_over(self, is_game_over: bool = True):
        """
        Создание состояния с установленным 
        флагом завершения игры
        """
        new_state = GameState(self.get_snake(), 
                              self.get_food_position(), 
                              self.get_score())
        new_state.paused = self.paused
        new_state.game_over = is_game_over
        new_state.quit_requested = self.quit_requested
        return new_state
    
    def with_quit_flag(self, should_quit: bool = True):
        """
        Создание состояния с установленным 
        флагом выхода
        """
        new_state = GameState(self.get_snake(), 
                              self.get_food_position(), 
                              self.get_score())
        new_state.paused = self.paused
        new_state.game_over = self.game_over
        new_state.quit_requested = should_quit
        return new_state
