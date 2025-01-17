## Caractéristiques du sondage

Je veux créer un sondage.
Le sondage est pour des utilisateurs non authentifiés : il doivent introduire leur nom (CharField) et une réponse pour chacun des items du sondage.

L'administrateur détermine les réponses possibles pour le sondage. Et il associe à chaque réponse une couleur. La limite max de réponses possibles est 10.

L'admin décide aussi si les utilisateurs peuvent voir le sondage : au moment où ils répondent, après avoir répondu ou pas du tout jusqu'à la fin du sondage.

L'admin dispose aussi de deux boutons pour : fermer le sondage et afficher les résultats.

Crée le snippet sondage, le block pour l'intégrer dans un streamfield, et le template.
Le template peut être divisé en plusieurs parties si besoin.

chaque sondage peut contenir plusieurs items/questions. Et l'utilisateur peut ou doit répondre à chacune d'entre elles individuellement, avec les possibilités données par l'admin.

L'admin peut décider si les réponses sont obligatoires ou non. Et il faut une validation dans le formulaire html en fonction.