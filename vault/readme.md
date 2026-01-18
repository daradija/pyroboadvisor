# Integración de un vault en PyRoboAdvisor

## Acceso al vault

Independientemente del proveedor usado siempre es necesario definir credenciales de acceso en algún lado. Si el despliegue se realiza en k8s o docker swarm se puede (y debe) usar el sistema de secrets, pero en un entorno con docker o ejecución directa es necesario definir en algún lado las credenciales de acceso o usar un agente que actúe como proxy para evitar la interacción del usuario.

En el caso de docker proponemos guardar las credenciales del vault en un volumen persistente. De esta manera herramientas como `docker inspect` no tienen acceso a ellas. Para hacerlo, en el yaml del docker hay que incluir:
``` yaml
volumes:
  - /opt/secrets/bw_clientid:/run/secrets/bw_clientid:ro
  - /opt/secrets/bw_clientsecret:/run/secrets/bw_clientsecret:ro
```
Los ficheros obviamente deben estar protegidos (sólo acceso por root) y deben seguir siempre el principio de mínimo acceso.

## Vaultwarden

[Vaultwarden](https://hub.docker.com/r/vaultwarden/server/) es una implementación en Rust de Bitwarden server y compatible con clientes [Bitwarden](https://bitwarden.com/).

Nota: Estas instrucciones asumen que hay un entorno Vaultwarden accesible desde donde se va a ejecutar pyroboadvisor.

En vaultwarden admin:
- Invita un usuario para la automatización. El correo no tiene que ser real. 

En vaultwarden:
- Crea la cuenta del usuario de automatización. Pon un password imposible, sólo se usara una vez. 
- Visualizar la API key en Settings / Security, tab Keys. Necesitarás el password imposible.
- Anota client_id y client_secret

En vaultwarden, accediendo con tu usuario:
- Crear organización 
- Crear collection (ej: pyroboadvisor)
- Crear las siguientes entradas:
  - pyroboadvisor
  - interactivebrokers.ie
  - gmail_app_pwd (opcional)
  - telegram_api_key (opcional) 
- Invita al usuario nuevo a la organización. Debes ir luego a Members y confirmar la invitación
- Concede permisos de view items

Más info en https://bitwarden.com/help/personal-api-key/

A falta de un cliente bitwarden oficial para ARM, se usa [python-bit-vault-warden-client](https://github.com/Q24/python-bit-vault-warden-client). Por tanto, hay que instalar el requirements.txt