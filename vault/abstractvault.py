from abc import ABC, abstractmethod

class AbstractVault(ABC):
    '''
    Clase abstracta que define la interfaz para interactuar con un vault
    '''

    @abstractmethod
    def get_credentials(self, name: str) -> tuple[str, str]:
        '''
        Devuelve las credenciales (usuario, contraseña) para la entrada en el vault
        
        :param name: Nombre de la entrada en el vault
        :return: Par de usuario y contraseña
        '''
        pass