## Pour ajouter une règle de firewall (Unbuntu)
```sh
sudo ufw enable

sudo ufw allow 25526/tcp
```
## Pour ajouter une règle sur le firewall (Debian)
⚠️Vous devez posséder le module iptables qui n'est pas forcément installé de base
```sh
iptables -A INPUT -p tcp –dport 2525 -j ACCEPT
service iptables save
```
## Concernant les règles de firewall (WINDOWS)
Sur windows c'est un peu différents 
Vous pouvez suivre ce tuto qui possède des images qui devraient bien vous orienter [Cliquez ici](https://creodias.eu/-/how-to-open-ports-in-windows-)
Ou alors l'enssembles de ces étapes
```diff
Dans le menu Démarrer , cliquez sur Panneau de configuration, cliquez sur Système et sécurité, puis sur Pare-feu Windows. Le Panneau de configuration n'est pas configuré pour l'affichage de « Catégorie », vous devez seulement sélectionner le Pare-feu Windows.

Cliquez sur Paramètres avancés.

Cliquez sur Règles de trafic entrant.

Cliquez sur Nouvelle règle dans la fenêtre Actions.

Cliquez sur Type de règle de Port.

Cliquez sur Suivant.

Dans la page Protocole et ports , cliquez sur TCP.

Sélectionnez Ports locaux spécifiques et tapez la valeur 25526.

Cliquez sur Suivant.

Dans la page Action , cliquez sur Autoriser la connexion.

Cliquez sur Suivant.

Dans la page Profil , cliquez sur les options appropriées pour votre environnement.

Cliquez sur Suivant.

Dans la page Nom , entrez un nom deReportServer (TCP sur le port 25526) .

Cliquez sur Terminer.

Redémarrez l'ordinateur.
```
