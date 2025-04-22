from locust import HttpUser, task, between
from random import randint

class DiososUser(HttpUser):
    wait_time = between(1, 5)  # Esperar entre 1 y 5 segundos entre tareas
    
    def on_start(self):
        """Se ejecuta cuando un usuario virtual comienza"""
        # Obtener una lista de IDs de dioses existentes
        response = self.client.get("/gods/")
        # En una aplicación real, aquí analizaríamos la respuesta para extraer los IDs
        # Para este ejemplo, simplemente asumimos que hay dioses con IDs del 1 al 5
        self.god_ids = list(range(1, 6))
    
    @task(3)
    def view_home(self):
        """Visitar la página de inicio (con prioridad 3)"""
        self.client.get("/")
    
    @task(5)
    def view_gods_list(self):
        """Visitar la lista de dioses por panteón (con prioridad 5)"""
        self.client.get("/gods/")
    
    @task(2)
    def view_random_god(self):
        """Visitar la página de detalle de un dios aleatorio (con prioridad 2)"""
        if self.god_ids:
            god_id = self.god_ids[randint(0, len(self.god_ids) - 1)]
            self.client.get(f"/god/{god_id}/")