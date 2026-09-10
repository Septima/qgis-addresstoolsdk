OBS - denne tekst er ved at blive opdateret til ny version af pluginet. Den nye version bliver snart tilgængelig via QGIS' plugin repository.

# Danske adresser i QGIS
## Hent pluginet fra QGIS plugin repository
Dette plugin kan hentes fra QGIS' officielle Plugin Repository direkte fra QGIS. Søg efter 'adresse', vælg 'Danish Address Tools' og klik på `Installér Plugin`

![QGISPluginRepository](./imgs/QGISPluginRepository.png)

(Dette billede skal opdateres til ny version)

Efter installation af plugin'et skal du sørge for, at “Processings-værktøjskassen” er vist - dette gøres fx fra menuen `Processering`.
I processeringsværktøjskassen findes adresseværktøjerne i gruppen 'Danske adresseværktøjer' --> Geokodning.

I øjeblikket indeholder pluginet ét værktøj: “Geokod danske adresser med Adressevask”.

![Værktøjskasse](./imgs/screendump.png)

(Dette billede skal opdateres til ny version)

## Geokod danske adresser med Adressevask
Dette værktøj bruges til at adressevaske og geokode et lag med adresser, så de vises som punkter på kortet.
Værktøjet anvender Klimadatastyrelsens <a href="https://confluence.kds.dk/display/ADV/Adressevask">Adressevask</a>- og <a href="https://confluence.kds.dk/pages/viewpage.action?pageId=246743156">Adressevælger</a>-API'er.

Pluginet oversætter en ustruktureret adressetekst til den officielle adresse i Danmarks Adresseregister (DAR). Det kan blandt andet håndtere stavefejl og adressetekster, hvor den officielle adressebetegnelse siden er blevet ændret.

![Værktøj til geokodning](./imgs/geokod.png)

(Dette billede skal opdateres til ny version)

### Adressetekster
Pluginet tager en adressetekst som input og returnerer den adresse, der bedst matcher. Hvis adressen er fordelt på flere felter i attributtabellen – fx vejnavn, husnummer og postnummer – kan felterne sættes sammen til ét samlet adresseudtryk ved hjælp af udtryksbyggeren (klik på epsilon-ikonet).

![Udtryksbygger](./imgs/Udtryksbygger.png)

Her er et eksempel, hvor adressen findes i de to felter "Vejnavn og vejnr" og "Postnummer". Funktionen Concat() bruges til at sammensætte disse to felter opdelt med et komma.
(Dette billede skal opdateres til ny version)

En gyldig adresse kan skrives på flere forskellige måder. Eksempelvis kan det supplerende bynavn udelades, eller det forkortede adresseringsvejnavn kan anvendes i stedet for det fulde vejnavn.

### Adressevaskede og geokodede resultater
Resultatet når pluginet køres er fire lag med de adressevaskede og geokodede resultater. Hvert lag indeholde de oprindelige felter, samt en række felter med resultater fra adressevasken og geokodningen.

Adressen vaskes og slås efterfølgende op hos Adressevælger i samme kald. Outputtet indeholder derfor både adresse-id, den fulde mængde af adresseoplysninger og adgangspunktets koordinater. Der er således ikke behov for et separat opslagsværktøj.

Adgangspunktets koordinater leveres i ETRS89 / UTM zone 32N (EPSG:25832).

#### Kvalitetsvurdering af den vaskede adresse:
Adressevaskens svar angiver, hvor sikkert adressen er matchet, ved hjælp af en vaskestatus-kode og -tekst, som erstatter DAWA's tidligere A/B/C-kategorier. Positive koder angiver forskellige grader af match, fx 1000, 900, 800 og 700, mens negative koder betyder, at adressen ikke kunne vaskes.

Vaskestatus_kode og vaskestatus_tekst tilføjes altid til outputtet – også når adressen ikke kunne vaskes. I disse tilfælde er de øvrige adressefelter og geometrien tomme.

Resultaterne fordeles på fire outputlag efter vaskestatus_kode, så de forskellige match kan kvalitetsvurderes separat:
- Kvalitet 1: kode 1000 – eksakt match
- Kvalitet 2: kode 900 – tilnærmet vejnavn
- Kvalitet 3: kode 700/800 – interval-adresse
- Fejl: negativ kode eller ingen adresse at vaske

De fire lag tilføjes til lagpanelet - også selvom de er tomme.

#### Historiske adresser
Adressevask anvender også DAR's historiske adresser som datagrundlag. Det betyder, at adressetekster med tidligere adressebetegnelser også kan matches.

Hvis adresseteksten matcher en historisk adressebetegnelse, angives den tidligere betegnelse i feltet historisk_adressebetegnelse. De øvrige adressefelter indeholder altid den aktuelle adressebetegnelse og de aktuelle adresseoplysninger.


### Testdata til afprøvning af pluginet
Du kan teste pluginet med dette demodatasæt, der indeholder adresser på en række biblioteker i København.
![Datasæt](./imgs/Biblioteker.txt)


### Forskelle i forhold til version 0.1 af pluginet
Der er en række forskelle i den nye version af pluginet. Nogle af forskellene er:
- I den tidligere version (0.1) var det muligt at vælge mellem vask af adresser eller adgangsadresser. Dette er ikke muligt i den nye version, da dette ikke indgår i den nye adressevasktjeneste.
- I den tidligere version var resultatet ét lag med alle adresser. I den nye version er resultaterne opdelt på fire lag.
- I den tidligere version blev der tilføjet fire feltet til attributtabellen i resultatet. I den nye version tilføjes en lang række felter.
- I den tidligere version blev hver adresse tildelt kategori A, B eller C alt efter hvor sikkert resulatet fra datavasken var. I den nye adressevasktjeneste er dette ændret til koder, hvor positive koder angiver forskellige grader af match, fx 1000, 900, 800 og 700, mens negative koder betyder, at adressen ikke kunne vaskes.


## Fejl eller ønsker til forbedring?
Oplever du en fejl i pluginet, så må du meget gerne oprettet en fejlbeskrivelse i pluginets <a href="https://github.com/Septima/qgis-addresstoolsdk/issues">Issuetracker</a>.

Har du en idé til en forbedring, så skriv til kontakt@septima.dk eller opret dit ønske i pluginets <a href="https://github.com/Septima/qgis-addresstoolsdk/issues">Issuetracker</a>. 

Septima vil med glæde tilbyde sin bistand til rettelser af fejl og forbedring.

I pluginets <a href="https://github.com/Septima/qgis-addresstoolsdk/issues">Issuetracker</a> kan du også se eksistrende registreringer af idéer og bugs.
