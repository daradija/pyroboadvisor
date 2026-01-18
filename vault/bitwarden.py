from bit_vault_warden_client import (WardenConfiguration, WardenAuthData,WardenClient, WardenCacheMode)
from vault.abstractvault import AbstractVault

class VaultwardenClient(AbstractVault):
    '''
    Implementación de AbstractVault para Vaultwarden
    '''
    PATH_CREDENCIALES="/run/secrets/"
    def __init__(self, url):
        auth_data = WardenAuthData(
            scope='api offline_access',
            client_id='web',
            grant_type='password',
            deviceType=9,
            deviceName='Bitwarden-Web-API'
        )

        config = WardenConfiguration(
            url=url,
            username=open(f"{self.PATH_CREDENCIALES}bw_clientid").read().strip(),
            password=open(f"{self.PATH_CREDENCIALES}bw_clientsecret").read().strip(),
            auth_data=auth_data,
            cache_mode=WardenCacheMode.FALLBACK, # Evitamos el uso de caché si hay conexión con el vault
            https_verify=False  # Desactivación de la verificación HTTPS para entornos selfhosting self-signed
        )
        self.client = WardenClient(config)

    def get_credentials(self, name: str) -> tuple[str, str]:
        result = self.client.fetch_credentials(name)
        username = result.raw_data["username"]
        password = result.raw_data["password"]
        return username, password
