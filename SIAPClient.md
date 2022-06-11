Pour tester SIAP Client dans un shell :

Ouvrir un shell django



Puis test de quelques appels:

>>> from core.siap_client.client import SIAPClient
>>> SIAPClient.get_instance().get_habilitations(user_login='nicolas.oudard@beta.gouv.fr')
