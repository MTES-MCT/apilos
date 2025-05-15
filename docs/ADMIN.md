```{toctree}
```

# Administration et back office

Différentes demandes au support nécessitent des interventions sur les données d'APiLos.

## Django admin

L'interface d'admin django (back office) est accessible à tous les utilisateurs `staff`, via l'url `/admin` L'équipe support est autonome pour réaliser des modifications en base de données manuellement via ce back office.

Si une modification demandée n'est pas possible dans l'admin, il faut arbitrer entre l'évolution de l'interface d'admin, ou la modification en shell de la donnée par un développeur

Lorsque la modification via l'admin prendrait trop de temps à l'équipe support, par exemple lorsqu'il y a beaucoup de volume à modifier, on passe plutôt par un script (shell ou commande)

## Détournement d'utilisateurs

La librairie `django-hijack` permet via l'admin de se connecter au site via le profil d'un utilisateur. C'est utile pour résoudre des problèmes liées aux habilitations des utilisateurs.

Pour détourner un utilisateur, aller dans l'admin à l'adresse `admin/users/user/`, rechercher l'utilisateur concerné et cliquer sur `détourner`

## Django shell

Pour une modification simple, on peut passer par un shell django via la commande :
`scalingo --region osc-fr1 -app apilos-siap-production run python manage.py shell`

Exemple d'utilisations de shell :

Le support transmet la demande "transférer toutes les conventions du bailleur x (siret 123) au bailleur y (siret 789)".

La modification sera la suivante :

```
from bailleurs.models import Bailleur
from programmes.models import Programme

old_bailleur = Bailleur.objects.get(siret="123")
old_bailleur  # Vérifier si le nom correspond

new_bailleur = Bailleur.objects.get(siret="789")
new_bailleur  # Vérifier si le nom correspond

programmes = Programme.objects.filter(bailleur=old_bailleur)
programmes.count()  # Pour s'assurer qu'on a bien filtré
programmes.update(bailleur=new_bailleur)
```

## Django commands

Pour une opération plus complexe, on est amené à écrire une commande django qui sera lancée de la même manière qu'un shell, via `python manage.py nom_de_la_commande`

Une commande permet de modifier un grand nombre d'entrées avec une gestion des erreurs. Par exemple pour réaliser l'update de status de conventions à partir d'un doc excel fourni par une DDT.

Une commande passe par une pull request qui sera review, mergée et déployée en production. Ce processsus prend  plus de temps qu'une modification en shell, mais permet une revue par les autres développeurs. C'est la méthode provilégiée pour toute opération lourde sur les données, pour garantir une relecture.
