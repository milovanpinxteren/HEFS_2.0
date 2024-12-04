Groups:
Kerstdiner
Pasen
Vaderdag
Moederdag
Customer (zelfde rechten als kerstdiner, pasen)
Finance
Analytics


Users: <br>
pasen2023 <br>
depaascateraar123

paasdiner2023 <br>
pasen123 <br>
## Database info
#### ApiUrls
api: <className> (e.g.: Paasdiner2023API())
user_id: id of corresponding user
begindatum: date of first order
organisatieIDs: {id1, id2}

#### AlgemeneInformatie
prognosegetal <br>
aantalHoofdgerechten <br>
aantalOrders


#### Shopify API
Apps en verkoopkanalen <br>
App maken <br>
configureren <br>
Toegangstoken beheerders API \
![img.png](img.png)


## Gerijptebieren
Add partner site to partner_sites and partner_websites

## Routing
Add the hub to orders with voornaam = 'Hub' and id 99999

## Configuring Dokku

- ssh-keygen -t ed25519
- copy .ssh/id_ed25519.pub to clipboard
- Login to host that runs dokku.
- sudo su
- Create temp file and paste ssh key
- dokku ssh-keys:add milo <temp file name>
- On dev machine, in folder with git repo:
- git remote add dokku dokku@89.145.161.168:hefs
- git push dokku
