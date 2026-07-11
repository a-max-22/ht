from typing import Tuple, List, Any, Optional
from core.torus import NTorus, TorusLoop
from core.base_types import Unit, unit, Product
from core.path import Path



class GameField:
    def __init__(self, width: int, height: int):
        """
        Инициализирует игровое поле как двумерный тор.
        
        Args:
            width: Ширина игрового поля.
            height: Высота игрового поля.
        """
        # Создаём 2D тор как базовую топологию для игры
        self.torus = NTorus(2)
        self.width = width
        self.height = height
    
    def get_dimensions(self) -> Tuple[int, int]:
        """Возвращает размеры игрового поля."""
        return (self.width, self.height)
    
    def create_position(self, x: int, y: int) -> Product:
        """
        Создаёт позицию на игровом поле, используя тип Product.
        
        Args:
            x: Координата X (будет закольцована в соответствии с топологией тора).
            y: Координата Y (будет закольцована в соответствии с топологией тора).
            
        Returns:
            Product, представляющий позицию (x, y).
        """
        # метод создает  координаты точки, выражая их через число "обходов" тора
        # для обеспечения совместимости, позиция точки выражается по старому 
        # как Product-тип из числа петель по каждому типу
        wrapped_x = x % self.width
        wrapped_y = y % self.height
        
        point_path = Path.refl(self.torus.base())
        for _ in range(0, wrapped_x):
            point_path = point_path.trans(self.torus.loop(0))

        for _ in range(0, wrapped_y):
            point_path = point_path.trans(self.torus.loop(1))

        torus_point = self.torus.encode_point(point_path)
        position_x, position_y = torus_point.counts
        
        return Product(position_x - 1, position_y - 1)
 
    
    def move_position(self, position: Product, dx: int, dy: int) -> Product:
        """
        Перемещает позицию на заданные дельты, учитывая топологию тора.
        
        Args:
            position: Текущая позиция в виде Product.
            dx: Изменение координаты X.
            dy: Изменение координаты Y.
            
        Returns:
            Новая позиция в виде Product.
        """
        x, y = position.first_value, position.second_value
        return self.create_position(x + dx, y + dy)
    
    def calculate_path(self, start: Product, end: Product) -> Path:
        """
        Создаёт Path между двумя позициями на игровом поле.
        
        Args:
            start: Начальная позиция.
            end: Конечная позиция.
            
        Returns:
            Path, представляющий движение от start до end.
        """
        return Path(start, end)
    
    def positions_equal(self, pos1: Product, pos2: Product) -> bool:
        """
        Проверяет, равны ли две позиции.
        
        Args:
            pos1: Первая позиция.
            pos2: Вторая позиция.
            
        Returns:
            True, если позиции равны, иначе False.
        """
        return pos1.first_value == pos2.first_value and pos1.second_value == pos2.second_value
    
