

## Algoritmer
Indtil videre udstiller denne provider én algoritme.

### Geokod danske adresser med DAWA
Denne algoritme anvender DAWAs Datavask-API.

Datavask-API'et gør det muligt at oversætte en ustruktureret adressetekst til en officiel, struktureret adresse med ID, også selvom adressen evt. indeholder en stavefejl eller den officielle adressebetegnelse er ændret.

Datavask-API'et anvendes ofte i en situation hvor man har tidligere indtastede adresser, som man ønsker at validere og evt. korrigere.

Datavask-API'et tager imod en adressetekst og returnerer den adresse, som bedst matcher adressen. Har anvenderen en struktueret adresse i forvejen skal anvenderen selv sammensætte adresseteksten.

Datavask svar indeholder en angivelse af hvor sikkert svaret er, anført som en kategori A, B eller C. Kategori A indikerer, at der er tale om et eksakt match. Kategori B indikerer, at der ikke er tale om et helt eksakt match, men at resultatet stadig er sikkert. Kategori C angiver, at resultatet usikkert.

Datavask anvender også historiske adresser som datagrundlag, således at adresser som er ændret også kan vaskes. Endvidere håndterer datavasken også adresser hvor der er anvendt stormodtagerpostnumre.

En gyldig adresse kan skrives på flere forskellige måder (varianter). Man kan vælge at udelade det supplerende bynavn, man kan benytte det forkorterede "adresseringsvejnavn" i stedet for det fulde vejnavn, og man kan anvende såkaldte "stormodtagerpostnumre". Datavask-resultatet angiver, hvilken variant af de mulige skrivemåder, som bedst matchede den angivne adressebetegnelse.

Bemærk, at der er separate API'er til vask af adresser og adgangsadresser. Forskellen på en adresse og en adgangsadresse er at adressen rummer eventuel etage- og/eller dørbetegnelse. Det gør adgangsadressen ikke.