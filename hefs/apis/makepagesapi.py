import datetime
import time

import requests
import spintax

# class MakePagesAPI():



    # def add_seo_pages(self):
        # def generate_synonyms(sentence):
        #     words = sentence.split()
        #     new_sentence = []
        #     for word in words:
        #         synonyms = []
        #         for syn in wordnet.synsets(word, lang='nld'):
        #             for lemma in syn.lemmas(lang='nld'):
        #                 synonyms.append(lemma.name())
        #         if synonyms:
        #             new_sentence.append(random.choice(synonyms))
        #         else:
        #             new_sentence.append(word)
        #     return ' '.join(new_sentence)
        # # nltk.download()
        #paasdiner api: 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
shopify_access_token = "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"
headers = {"Accept": "application/json", "Content-Type": "application/json",
           "X-Shopify-Access-Token": "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"}
places_array = [
    "Zeewolde",
    "Brummen",
    "Druten",
    "Nijkerk",
    "Nijmegen",
    "Wageningen",
    "Aalten",
    "Heumen",
    "Voorst",
    "Zevenaar",
    "Ede",
    "Geldermalsen",
    "Buren",
    "Putten",
    "Berkelland",
    "Epe",
    "Barneveld",
    "Culemborg",
    "Zutphen",
    "Montferland",
    "Overbetuwe",
    "Apeldoorn",
    "Doetinchem",
    "Hattem",
    "Tiel",
    "Lochem",
    "Duiven",
    "Winterswijk",
    "Westervoort",
    "Harderwijk",
    "Heerde",
    "Elburg",
    "Zaltbommel",
    "Oldebroek",
    "Zeewolde",
    "Brummen",
    "Scherpenzeel",
    "Oude IJsselstreek",
    "Rijnwaarden",
    "Druten",
    "Neerijnen",
    "Maasdriel",
    "Lingewaal",
    "Lingewaard",
    "Rheden",
    "Renkum",
    "Rozendaal",
    "West Maas en Waal",
    "Wijchen",
    "Aalten",
    "Heumen",
    "Enschede",
    "Zwolle",
    "Deventer",
    "Hengelo",
    "Almelo",
    "Kampen",
    "Raalte",
    "Oldenzaal",
    "Borne",
    "Dalfsen",
    "Steenwijkerland",
    "Hellendoorn",
    "Rijssen-Holten",
    "Wierden",
    "Twenterand",
    "Haaksbergen",
    "Ommen",
    "Tubbergen",
    "Zwartewaterland",
    "Hof van Twente",
    "Dinkelland",
    "Staphorst",
    "Losser",
    "Olst-Wijhe",
    "Nijverdal",
    "Vriezenveen",
    "Genemuiden",
    "Wijhe",
    "Lemelerveld",
    "Denekamp",
    "Diepenheim",
    "Markelo",
    "Bathmen",
    "Ootmarsum",
    "Holten",
    "Goor",
    "Vroomshoop",
    "Lemele",
    "Hardenberg",
    "Heino",
    "Enter",
    "Wanneperveen",
    "Giethoorn",
    "Zalk",
    "Hasselt",
    "Delden",
    "Nieuwleusen",
    "De Krim",
    "Hoonhorst",
    "Balkbrug",
    "Slagharen",
    "Hasselt",
    "Dedemsvaart",
    "Wanneperveen",
    "Giethoorn",
    "Westerhaar-Vriezenveensewijk",
    "Laag Zuthem",
    "Wilsum",
    "Bergentheim",
    "Lutten",
    "Langeveen",
    "Agelo",
    "Kamperzeedijk",
    "Saasveld",
    "Daarle",
    "Westerhaar",
    "Heeten",
    "Luttenberg",
    "Zalk",
    "Vinkenbuurt",
    "Laag Zuthem",
    "Wanneperveen",
    "Laag-Soeren",
    "Wilsum",
    "Ane",
    "Kamperzeedijk-Oost",
    "Holthone",
    "Rheeze",
    "De Pol",
    "Wielen",
    "Hezingen",
    "Rossum",
    "Bentelo",
    "Basse",
    "Haarle",
    "Holtheme",
    "Tilligte",
    "Mander",
    "Rheeze",
    "Willemsoord",
    "Vasse",
    "Haarle",
    "Den Ham",
    "Rouveen",
    "Hengelo",
    "Dedemsvaart",
    "Hezingen",
    "Westerhaar-Vriezenveensewijk",
    "Lemele",
    "Luttenberg",
    "Daarle",
    "Hoge Hexel",
    "Assen",
    "Emmen",
    "Hoogeveen",
    "Coevorden",
    "Meppel",
    "Borger-Odoorn",
    "Midden-Drenthe",
    "Tynaarlo",
    "De Wolden",
    "Emmen",
    "Aa en Hunze",
    "Westerveld",
    "Noordenveld",
    "Borger-Odoorn",
    "Midden-Drenthe",
    "Tynaarlo",
    "Coevorden",
    "Hoogeveen",
    "Meppel",
    "De Wolden",
    "Assen",
    "Borger",
    "Anloo",
    "Norg",
    "Dwingeloo",
    "Beilen",
    "Roden",
    "Smilde",
    "Schoonebeek",
    "Sleen",
    "Vries",
    "Eelde",
    "Rolde",
    "Westerbork",
    "Diever",
    "Ruinen",
    "Ees",
    "Witteveen",
    "Exloo",
    "Bovensmilde",
    "Gieten",
    "Elim",
    "Annen",
    "Odoorn",
    "Aalden",
    "Gasselte",
    "Peize",
    "Eext",
    "Zuidlaren",
    "Barger-Compascuum",
    "Eesergroen",
    "Wezuperbrug",
    "Schoonoord",
    "Noord-Sleen",
    "Drouwen",
    "Nieuw-Amsterdam",
    "Dalerveen",
    "Hollandscheveld",
    "Nieuw-Balinge",
    "Valthermond",
    "Hijken",
    "Hoogersmilde",
    "Pesse",
    "Gasselternijveenschemond",
    "Musselkanaal",
    "Balinge",
    "Nieuw-Dordrecht",
    "Wijster",
    "Westersebos",
    "Sleen",
    "Barger-Oosterveld",
    "Bunne",
    "Eursinge",
    "Deurze",
    "Tweede Valthermond",
    "Nieuw-Weerdinge",
    "Balloërveld",
    "Alteveer",
    "Schoonloo",
    "Zuidveld",
    "Wijster",
    "Eeserveen",
    "Weiteveen",
    "Drijber",
    "Schoonloo",
    "Oosterhesselen",
    "Eeserveen",
    "Witteveen",
    "Balloërveld",
    "De Kiel",
    "Witteveen",
    "Eesergroen",
    "Nieuwlande",
    "Diphoorn",
    "Drijber",
    "Oosterhesselen",
    "Aalden",
    "De Kiel",
    "Noord-Sleen",
    "Amen",
    "Wachtum",
    "Groningen",
    "Delfzijl",
    "Veendam",
    "Hoogezand-Sappemeer",
    "Winsum",
    "Stadskanaal",
    "Oldambt",
    "Haren",
    "Bedum",
    "Appingedam",
    "Zuidhorn",
    "Loppersum",
    "Ten Boer",
    "Slochteren",
    "De Marne",
    "Grootegast",
    "Eemsmond",
    "Menterwolde",
    "Vlagtwedde",
    "Leek",
    "Marum",
    "Zuidhorn",
    "Ezinge",
    "Delfzijl",
    "Stadskanaal",
    "Slochteren",
    "Hoogezand-Sappemeer",
    "Grootegast",
    "Appingedam",
    "Winsum",
    "De Marne",
    "Bedum",
    "Ten Boer",
    "Veendam",
    "Loppersum",
    "Oldambt",
    "Menterwolde",
    "Vlagtwedde",
    "Leek",
    "Marum",
    "Haren",
    "Eemsmond",
    "Zuidbroek",
    "Baflo",
    "Zuidwolde",
    "Musselkanaal",
    "Onstwedde",
    "Grijpskerk",
    "Zuidlaren",
    "Nieuwe Pekela",
    "Eelde",
    "Sappemeer",
    "Zuidbroek",
    "Muntendam",
    "Scheemda",
    "Stedum",
    "Middelstum",
    "Siddeburen",
    "Bellingwolde",
    "Scharmer",
    "Glimmen",
    "Zuidlaarderveen",
    "Finsterwolde",
    "Eenrum",
    "Vriescheloo",
    "Noordbroek",
    "Bourtange",
    "Oude Pekela",
    "Noordhorn",
    "Groningen",
    "Kloosterburen",
    "Spijk",
    "Veele",
    "Winneweer",
    "Sellingen",
    "Noordlaren",
    "Garnwerd",
    "Westerbroek",
    "Drieborg",
    "Wedde",
    "Warffum",
    "Meeden",
    "Farmsum",
    "Zuidhorn",
    "Pieterburen",
    "Wagenborgen",
    "Oostwold",
    "Adorp",
    "Nieuweschans",
    "Hoogkerk",
    "Bad Nieuweschans",
    "Bierum",
    "Eelde-Paterswolde",
    "Froombosch",
    "Winsum",
    "Kolham",
    "Slochteren",
    "Borgsweer",
    "Leeuwarden",
    "Heerenveen",
    "Drachten",
    "Sneek",
    "Harlingen",
    "Smallingerland",
    "De Fryske Marren",
    "Waadhoeke",
    "Tytsjerksteradiel",
    "Achtkarspelen",
    "Opsterland",
    "Dantumadiel",
    "Schiermonnikoog",
    "Ooststellingwerf",
    "Weststellingwerf",
    "Súdwest-Fryslân",
    "Ferwerderadiel",
    "Noardeast-Fryslân",
    "Kollumerland en Nieuwkruisland",
    "Ameland",
    "Terschelling",
    "Harlingen",
    "Leeuwarden",
    "Súdwest-Fryslân",
    "Achtkarspelen",
    "Noardeast-Fryslân",
    "Smallingerland",
    "De Fryske Marren",
    "Opsterland",
    "Ferwerderadiel",
    "Heerenveen",
    "Ooststellingwerf",
    "Weststellingwerf",
    "Waadhoeke",
    "Tytsjerksteradiel",
    "Dantumadiel",
    "Kollumerland en Nieuwkruisland",
    "Dongeradeel",
    "Tytsjerksteradiel",
    "Weststellingwerf",
    "Smallingerland",
    "De Fryske Marren",
    "Waadhoeke",
    "Heerenveen",
    "Opsterland",
    "Achtkarspelen",
    "Dantumadiel",
    "Súdwest-Fryslân",
    "Noardeast-Fryslân",
    "Ooststellingwerf",
    "Harlingen",
    "Ferwerderadiel",
    "Kollumerland en Nieuwkruisland",
    "Ameland",
    "Terschelling",
    "Schiermonnikoog",
    "Vlieland",
    "Bolsward",
    "Dokkum",
    "Franeker",
    "Joure",
    "Wolvega",
    "Sneek",
    "Lemmer",
    "Grou",
    "Workum",
    "Berlikum",
    "Sint Annaparochie",
    "Damwoude",
    "Makkum",
    "Stiens",
    "Burgum",
    "Buitenpost",
    "Oosterwolde",
    "Drachten",
    "Harlingen",
    "Leeuwarden",
    "Heerenveen",
    "Sneek",
    "Dokkum",
    "Wolvega",
    "Bolsward",
    "Franeker",
    "Joure",
    "Lemmer",
    "Sint Nicolaasga",
    "Grou",
    "Koudum",
    "Hindeloopen",
    "Sint Annaparochie",
    "Workum",
    "Damwoude",
    "Stiens",
    "Balk",
    "Wommels",
    "Burgum",
    "Buitenpost",
    "Makkum",
    "Hallum",
    "Oosterwolde",
    "Rijperkerk",
    "Berlikum",
    "Bergum",
    "Dronrijp",
    "Sint Jacobiparochie",
    "Hallum",
    "Sint Nicolaasga",
    "Hallum",
    "Gytsjerk",
    "Kootstertille",
    "Almere",
    "Lelystad",
    "Dronten",
    "Noordoostpolder",
    "Zeewolde",
    "Urk",
    "Zeewolde",
    "Lelystad",
    "Almere",
    "Dronten",
    "Noordoostpolder",
    "Urk",
    "Biddinghuizen",
    "Swifterbant",
    "Emmeloord",
    "Lelystad",
    "Almere",
    "Dronten",
    "Noordoostpolder",
    "Urk",
    "Zeewolde",
    "Biddinghuizen",
    "Swifterbant",
    "Nagele",
    "Creil",
    "Emmeloord",
    "Ens",
    "Tollebeek",
    "Espel",
    "Marknesse",
    "Rutten",
    "Luttelgeest",
    "Kraggenburg",
    "Lelystad",
    "Almere",
    "Dronten",
    "Noordoostpolder",
    "Urk",
    "Zeewolde",
    "Biddinghuizen",
    "Swifterbant",
    "Nagele",
    "Emmeloord",
    "Creil",
    "Tollebeek",
    "Ens",
    "Espel",
    "Marknesse",
    "Rutten",
    "Luttelgeest",
    "Kraggenburg",
    "Dronten",
    "Biddinghuizen",
    "Swifterbant",
    "Lelystad",
    "Almere",
    "Emmeloord",
    "Noordoostpolder",
    "Urk",
    "Zeewolde",
    "Nagele",
    "Creil",
    "Tollebeek",
    "Espel",
    "Marknesse",
    "Rutten",
    "Luttelgeest",
    "Kraggenburg",
    "Dronten",
    "Biddinghuizen",
    "Swifterbant",
    "Urk",
    "Lelystad",
    "Almere",
    "Emmeloord",
    "Noordoostpolder",
    "Zeewolde",
    "Nagele",
    "Creil",
    "Tollebeek",
    "Espel",
    "Marknesse",
    "Rutten",
    "Luttelgeest",
    "Kraggenburg",
    "Dronten",
    "Biddinghuizen",
    "Swifterbant",
    "Emmeloord",
    "Urk",
    "Lelystad",
    "Almere",
    "Noordoostpolder",
    "Zeewolde",
    "Nagele",
    "Creil",
    "Tollebeek",
    "Espel",
    "Marknesse",
    "Rutten",
    "Luttelgeest",
    "Kraggenburg"
]
# places_array = ['Vinkel']
place = 'test'
seo_teksten_array = [
    f"""
            Geniet van een onvergetelijk kerstdiner aan huis in {place}!

        Maak dit kerstfeest extra speciaal en stressvrij door een heerlijk kerstdiner aan huis te bestellen in {place}. Bij kerstdiner.nl begrijpen we dat de feestdagen draaien om quality time met je dierbaren. Daarom bieden wij een uitgebreid assortiment van culinaire hoogstandjes die met liefde zijn bereid door onze getalenteerde chef-koks.

        Met ons kerstdiner aan huis service hoef je je geen zorgen te maken over de boodschappen, het bereiden van ingewikkelde recepten of de afwas. Onze professionele cateraars zorgen voor alles, zodat jij je kunt focussen op het vieren van een magische kerst.

        Ons menu voor het kerstdiner aan huis is samengesteld met de fijnste ingrediënten en biedt een ruime keuze aan heerlijke gerechten. Van smaakvolle voorgerechten tot verfijnde hoofdgerechten en verrukkelijke desserts, we hebben voor ieder wat wils. Onze menu's zijn met zorg samengesteld om je smaakpapillen te verwennen en te zorgen voor een onvergetelijke culinaire ervaring.

        Het bestellen van je kerstdiner aan huis in {place} is eenvoudig. Bezoek onze website, bekijk ons uitgebreide menu en kies je favoriete gerechten. Plaats eenvoudig je bestelling en geef de gewenste leverdatum en -tijd door. Wij zorgen ervoor dat je kerstdiner op het afgesproken tijdstip wordt bezorgd, zorgvuldig verpakt en klaar om te worden genoten.

        Of je nu met je gezin, vrienden of collega's samenkomt, ons kerstdiner aan huis zorgt voor een feestelijke sfeer en heerlijke maaltijden. Creëer nieuwe herinneringen, geniet van elkaars gezelschap en laat ons voor de culinaire magie zorgen.

        Wacht niet langer en bestel vandaag nog je kerstdiner aan huis in {place} bij kerstdiner.nl. Maak van deze kerst een feest om nooit te vergeten!
            """,

    f"""
            Kerstdiner bestellen op locatie? Ontdek de culinaire mogelijkheden bij kerstdiner.nl in {place}!

        Maak van dit kerstseizoen een onvergetelijke ervaring door je kerstdiner op locatie te bestellen bij kerstdiner.nl in {place}. Bij kerstdiner.nl begrijpen we de betekenis van de feestdagen en willen we jou en je gasten laten genieten van heerlijke maaltijden zonder stress en gedoe.

        Met ons uitgebreide assortiment van smaakvolle gerechten en professionele cateringdiensten zorgen we ervoor dat je kerstdiner op locatie een culinair hoogtepunt wordt. Onze ervaren chef-koks bereiden met liefde en vakmanschap de meest verrukkelijke voorgerechten, smaakvolle hoofdgerechten en heerlijke desserts.

        Bij kerstdiner.nl begrijpen we dat elk evenement uniek is, daarom bieden we flexibele opties om je kerstdiner op locatie aan te passen aan je wensen en behoeften. Of je nu een intiem diner met je naaste familie of een groot feest met vrienden en collega's organiseert, we zorgen voor een gastronomische ervaring die bij jouw evenement past.

        Het bestellen van je kerstdiner op locatie is eenvoudig bij kerstdiner.nl. Bezoek onze website, ontdek ons gevarieerde menu en kies je favoriete gerechten. Plaats eenvoudig je bestelling en geef de gewenste locatie, datum en tijd door. Wij zorgen ervoor dat je kerstdiner op het afgesproken moment en op de door jou gekozen locatie wordt bezorgd, zorgvuldig verpakt en klaar om van te genieten.

        Of je nu thuis, op kantoor of op een andere locatie in {place} wilt genieten van een heerlijk kerstdiner, kerstdiner.nl staat voor je klaar. Laat ons de culinaire zorgen uit handen nemen, zodat jij kunt genieten van een zorgeloos en smaakvol kerstfeest op jouw gewenste locatie.

        Wacht niet langer en bestel vandaag nog je kerstdiner op locatie bij kerstdiner.nl in {place}. Maak van deze kerst een gastronomisch festijn om nooit te vergeten!
            """,
    f"""
        Kerstbrunch aan huis bestellen in {place}? Ontdek de culinaire mogelijkheden bij kerstdiner.nl!

        Maak dit kerstseizoen extra feestelijk en gemakkelijk door je kerstbrunch aan huis te bestellen in {place}. Bij kerstdiner.nl begrijpen we dat de feestdagen draaien om samenzijn en genieten van heerlijk eten. Daarom bieden wij een uitgebreid assortiment van smaakvolle gerechten die met liefde zijn bereid door onze professionele koks.

        Met onze kerstbrunch aan huis service hoef je je geen zorgen te maken over het bereiden van ingewikkelde recepten, de boodschappen of de tafeldekking. Onze culinaire experts zorgen voor alles, zodat jij en je gasten optimaal kunnen genieten van een ontspannen kerstbrunch.

        Ons menu voor de kerstbrunch aan huis is met zorg samengesteld en biedt een ruime keuze aan heerlijke gerechten. Van verse broodjes en luxe beleg tot hartige quiches, salades en smakelijke zoetigheden, ons menu is een waar feest voor de smaakpapillen. Al onze gerechten worden bereid met hoogwaardige ingrediënten en zijn met oog voor detail samengesteld.

        Het bestellen van je kerstbrunch aan huis in {place} is eenvoudig bij kerstdiner.nl. Bezoek onze website, bekijk ons uitgebreide menu en maak je keuze uit de heerlijke brunchopties. Plaats eenvoudig je bestelling en geef de gewenste leverdatum en -tijd door. Wij zorgen ervoor dat je kerstbrunch op het afgesproken moment wordt bezorgd, zorgvuldig verpakt en klaar om van te genieten.

        Of je nu thuis, op kantoor of op een andere locatie in {place} wilt genieten van een heerlijke kerstbrunch, kerstdiner.nl staat voor je klaar. Laat ons de culinaire zorgen uit handen nemen, zodat jij kunt genieten van een zorgeloze en smaakvolle kerstbrunch op jouw gewenste locatie.

        Wacht niet langer en bestel vandaag nog je kerstbrunch aan huis in {place} bij kerstdiner.nl. Maak van deze kerst een culinair festijn om nooit te vergeten!
        """,
    f"""
        Kerstbrunch bestellen op locatie? Ontdek de feestelijke mogelijkheden bij kerstdiner.nl in {place}!

        Maak van deze kerst een culinair feest en bestel je kerstbrunch op locatie bij kerstdiner.nl in {place}. Bij kerstdiner.nl begrijpen we dat de feestdagen draaien om gezelligheid en genieten van heerlijk eten. Daarom bieden wij een uitgebreide selectie van smaakvolle gerechten, speciaal samengesteld voor een feestelijke kerstbrunch.

        Met onze kerstbrunch bestelservice op locatie kun je zorgeloos genieten van een heerlijke maaltijd met je dierbaren. Onze professionele koks bereiden met passie en vakmanschap een assortiment van heerlijke gerechten, variërend van verse broodjes en hartige quiches tot kleurrijke salades en verrukkelijke zoetigheden.

        Het bestellen van je kerstbrunch op locatie is eenvoudig bij kerstdiner.nl. Bezoek onze website, bekijk ons uitgebreide menu en maak je keuze uit de diverse brunchopties. Plaats eenvoudig je bestelling en geef de gewenste leverdatum en -tijd door. Wij zorgen ervoor dat je kerstbrunch op het afgesproken tijdstip wordt bezorgd op de door jou gekozen locatie, zorgvuldig verpakt en klaar om van te genieten.

        Of je nu thuis, op kantoor of op een andere locatie in {place} wilt genieten van een smaakvolle kerstbrunch, kerstdiner.nl staat voor je klaar. Laat ons de culinaire invulling van je kerst verzorgen, zodat jij volop kunt genieten van een ontspannen en smaakvolle kerstviering op jouw gewenste locatie.

        Wacht niet langer en bestel vandaag nog je kerstbrunch op locatie bij kerstdiner.nl in {place}. Maak van deze kerst een onvergetelijke culinaire ervaring!
        """,
    f"""
        Kerst catering op locatie bestellen in {place}? Ontdek de smaakvolle mogelijkheden bij kerstdiner.nl!

        Maak je kerstviering extra bijzonder en gemakkelijk met onze kerst catering op locatie in {place}. Bij kerstdiner.nl begrijpen we dat de feestdagen draaien om samenzijn en genieten van heerlijk eten. Daarom bieden wij een uitgebreide selectie van culinaire hoogstandjes die met liefde en vakmanschap zijn bereid.

        Onze kerst catering op locatie service zorgt ervoor dat je kerstdiner een onvergetelijke ervaring wordt, waarbij je gasten worden verwend met smaakvolle gerechten. Onze ervaren chefs creëren een uniek menu met een combinatie van verfijnde smaken en traditionele favorieten, zodat je kunt genieten van een authentieke en smaakvolle kerstbeleving.

        Met onze kerst catering op locatie nemen we alle zorgen uit handen. Of je nu een intiem diner thuis, een bedrijfsevenement of een feestelijke bijeenkomst organiseert, ons team zorgt voor een naadloze en professionele service. Wij leveren het kerstdiner op de door jou gekozen locatie, zodat jij je kunt concentreren op het creëren van mooie herinneringen met je dierbaren.

        Het bestellen van onze kerst catering op locatie is eenvoudig. Bezoek onze website, ontdek ons uitgebreide menu en maak je keuze uit de heerlijke gerechten. Plaats je bestelling en geef de gewenste leverdatum en -tijd door. Wij zorgen ervoor dat je kerstdiner op locatie wordt bezorgd, zorgvuldig verpakt en klaar om van te genieten.

        Of je nu een klassieke kerstmaaltijd, een verrassend buffet of een luxueus diner op locatie wilt, kerstdiner.nl staat voor je klaar. Laat ons de culinaire invulling van je kerst verzorgen, terwijl jij geniet van een zorgeloze en smaakvolle kerstviering op jouw gewenste locatie.

        Wacht niet langer en bestel vandaag nog je kerst catering op locatie bij kerstdiner.nl in {place}. Maak van deze kerst een onvergetelijke culinaire ervaring!
        """,
    f"""
        Op zoek naar een traiteur voor kerst in {place}? Ontdek de culinaire mogelijkheden bij kerstdiner.nl!

        Maak van je kerstviering een smaakvol feest met de traiteurdiensten van kerstdiner.nl in {place}. Bij kerstdiner.nl begrijpen we dat de feestdagen draaien om samenzijn en genieten van heerlijk eten. Daarom bieden wij een uitgebreide selectie van hoogwaardige gerechten, bereid door onze ervaren traiteurs.

        Met onze traiteurdiensten voor kerst op locatie hoef je je geen zorgen te maken over de culinaire invulling van je feest. Onze professionele traiteurs zorgen voor een smaakvolle en gastronomische ervaring, waarbij elk gerecht met zorg en aandacht wordt bereid. Laat ons je verrassen met een uniek en feestelijk menu dat perfect past bij jouw kerstviering.

        Onze traiteurmenu's voor kerst bieden een verscheidenheid aan culinaire hoogstandjes. Van verfijnde amuse-gueules tot heerlijke voorgerechten, smaakvolle hoofdgerechten en verrukkelijke desserts, ons menu zal zelfs de meest veeleisende fijnproevers tevredenstellen. We maken gebruik van de beste ingrediënten en kiezen voor seizoensgebonden producten om de smaak en versheid te waarborgen.

        Het bestellen van onze traiteurdiensten voor kerst op locatie is eenvoudig. Bezoek onze website, bekijk ons gevarieerde menu en maak je keuze uit de heerlijke gerechten. Plaats je bestelling en geef de gewenste leverdatum en -tijd door. Wij zorgen ervoor dat je kerstdiner op locatie wordt bezorgd, zorgvuldig verpakt en klaar om van te genieten.

        Of je nu thuis, op kantoor of op een andere locatie in {place} wilt genieten van een exclusieve kerstervaring, kerstdiner.nl staat voor je klaar. Laat ons de culinaire invulling van je kerst verzorgen, terwijl jij en je gasten ontspannen en genieten van een onvergetelijke kerstviering.

        Wacht niet langer en bestel vandaag nog je traiteur voor kerst bij kerstdiner.nl in {place}. Maak van deze kerst een culinair festijn om nooit te vergeten!
        """
]

seo_teksten_array = [
    "{Bestel nu en geniet van een heerlijke|Laat de paasvreugde thuisbezorgen met onze smakelijke|Proef de verrukking van een exclusieve} paasbrunch in {place}. Onze ervaren chefs hebben met zorg een menu samengesteld vol met {verfijnde gerechten|exclusieve lekkernijen|heerlijke specialiteiten}. Van {hartige hapjes|luxe voorgerechten|culinaire hoogstandjes} tot {zoete verleidingen|ambachtelijke desserts|hemelse zoetigheden}, er is voor elk wat wils. Bestel vandaag nog en laat de paassfeer bij u thuis bezorgen!",
    "{Begin de paasdag met een verrukkelijk|Geniet van een uitgebreid en smaakvol|Laat u verwennen met een heerlijk} paasontbijt, thuisbezorgd in {place}. Onze ontbijtselectie bevat een scala aan {verse|ambachtelijke|biologische} ingrediënten, waardoor uw ochtend een ware {culinaire|feestelijke|gezellige} ervaring wordt. Bestel uw ontbijt en breng samen met vrienden en familie een ontspannen paasochtend door in {place}!",
    "{Vier Pasen op unieke wijze bij ons|Ervaar een onvergetelijke Paasviering met onze speciale|Maak Pasen extra speciaal met een} paasviering, thuisbezorgd in {place}. Onze {smakelijke brunches|culinaire hoogstandjes|uitgebreide buffetten} en {feestelijke diners|speciale menu's|gezellige ontbijten} bieden een scala aan opties voor een onvergetelijke dag. Ontdek de unieke sfeer van Pasen in {place} en bestel uw paasmaaltijd voor thuisbezorging!",
    "{Nodig vrienden en familie uit voor een smaakvol|Maak van Pasen een bijzonder feest met een gezellig|Organiseer een onvergetelijk} paasfeest thuis in {place}. Geniet samen van een {overvloedige brunch|heerlijk ontbijt|feestelijk diner} en laat {place} het decor zijn van uw vreugdevolle paasviering. Bestel uw paasmaaltijd en creëer mooie herinneringen tijdens deze speciale tijd van het jaar!"
                     ]

id = 143092082
count = 0
title_dict = {1: 'Paasontbijt aan huis', 2: 'Paasbrunch bestellen', 3: 'Paasbrunch aan huis',
              4: 'Paasbrunch bestellen', 5: 'Pasen catering', 6: 'Trateur Pasen'}
for place in places_array:
    tekst_nr = 0
    for tekst in seo_teksten_array:
        tekst_nr += 1
        general_tekst = tekst.replace('{place}', place)
        final_text = spintax.spin(general_tekst)
        # specific_tekst = generate_synonyms(general_tekst)
        # print(specific_tekst)
        id += 1
        title = title_dict[tekst_nr] + ' ' + place

        payload = {
            "page": {
                "author": "kerstdiner.nl",
                "body_html": final_text,
                "created_at": str(datetime.datetime.now()),
                "handle": "" + title.replace(' ', '-'),
                "id": id,
                "metafield": {
                    "key": "new",
                    "value": "new value",
                    "type": "single_line_text_field",
                    "namespace": "global"
                },
                "published_at": str(datetime.datetime.now()),
                "shop_id": 548380009,
                "template_suffix": "about",
                "title": title,
                "updated_at": str(datetime.datetime.now()),
                "admin_graphql_api_id": "gid://shopify/OnlineStorePage/" + str(id)
            }
        }
        time.sleep(1)
        count += 1
        response = requests.post(url="https://b88885-3.myshopify.com/admin/api/2023-04/pages.json",
                                 headers=headers,
                                 json=payload)
        print(response, count)