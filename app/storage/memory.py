from typing import Dict, List
from app.models.product import Product


class ProductStorage:
    """
    Sistema de almacenamiento en memoria para productos.
    
    Mantiene los productos en un diccionario durante la ejecución de la aplicación.
    Genera IDs únicos automáticamente para cada producto agregado.
    """
    
    def __init__(self):
        """Inicializa el almacenamiento vacío."""
        self.products: Dict[int, Product] = {}
        self.next_id: int = 1
    
    def add(self, product: Product) -> Product:
        """
        Agrega un producto al almacenamiento y le asigna un ID único.
        
        Args:
            product: Producto a agregar (sin ID o con ID que será reemplazado)
        
        Returns:
            Product: El producto con su ID asignado
        """
        # Asignar ID único al producto
        product.id = self.next_id
        
        # Almacenar el producto
        self.products[self.next_id] = product
        
        # Incrementar el contador para el próximo ID
        self.next_id += 1
        
        return product
    
    def get_all(self) -> List[Product]:
        """
        Retorna todos los productos almacenados.
        
        Returns:
            List[Product]: Lista de todos los productos en el almacenamiento
        """
        return list(self.products.values())
