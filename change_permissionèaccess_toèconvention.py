>>> from programmes.models import  Programme
>>> from bailleurs.models import Bailleur
>>>
>>> from conventions.models import Convention
>>>
>>> old_b = bailleur.objects.get(siren='477976773')
>>> old_b = Bailleur.objects.get(siren='477976773')
>>> old_b
<Bailleur: O.P.H. DE COMMENTRY (477976773)>
>>> new_b = Bailleur.objects.get(siren='598201325')
>>> convs = Convention.objects.get(uuid='0b91d3ad-248b-475e-ae80-64af4ef8b9fb')
>>> convs
<Convention: Commentry - COMMENTRY - RUE DU 4 SEPTEMBRE - 67 LGTS - 67 lgts - Collectif - PLUS>
>>> convs.programme.bailleur = new_b
>>> convs.programme.save()
>>>
>>> avenants = Conventions.objects.filter(parent=convs)
Traceback (most recent call last):
  File "/app/.scalingo/python/lib/python3.12/code.py", line 90, in runcode
    exec(code, self.locals)
  File "<console>", line 1, in <module>
NameError: name 'Conventions' is not defined. Did you mean: 'Convention'?
>>> avenants = Convention.objects.filter(parent=convs)
>>> avenants.count()
3
>>> avenants
<ConventionQuerySet [<Convention: Commentry - COMMENTRY - RUE DU 4 SEPTEMBRE - 67 LGTS - 37 lgts - Collectif - PLUS>, <Convention: Commentry - COMMENTRY - RUE DU 4 SEPTEMBRE - 67 LGTS - 67 lgts - Collectif - PLUS>, <Convention: Commentry - COMMENTRY - RUE DU 4 SEPTEMBRE - 67 LGTS - 67 lgts - Collectif - PLUS>]>
>>> last_avenant = avenants.order_by('~televersement_convention_signee_le').first()
>>> last_avenant = avenants.order_by('-televersement_convention_signee_le').first()
>>> last_avenant
<Convention: Commentry - COMMENTRY - RUE DU 4 SEPTEMBRE - 67 LGTS - 37 lgts - Collectif - PLUS>
>>> last_avenant.numero
'3'
>>> last_avenant.programme.baileur
>>> last_avenant.programme
<Programme: COMMENTRY - RUE DU 4 SEPTEMBRE - 67 LGTS>
>>> last_avenant.programme.bailleur
<Bailleur: O.P.H. DE COMMENTRY (477976773)>
>>> last_avenant.programme.bailleur = new_b
>>> last_avenant.programme.bailleur
<Bailleur: EVOLEA (598201325)>
>>> last_avenant.programme.save()