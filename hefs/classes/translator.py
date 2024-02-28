from deep_translator import GoogleTranslator

class Translator():
    def translate_from_google(self, domain, text_to_translate):
        domain_language_dict = {'387f61-2.myshopify.com': 'de'}
        target_language = domain_language_dict[domain]
        translated_text = GoogleTranslator(soruce='auto', target=target_language).translate(text_to_translate)
        return translated_text

    def translate_value_from_dict(self, domain, key, value):
        if domain == '387f61-2.myshopify.com': #german website
            if key == 'land_van_herkomst':
                translation_dict = {"België": "Belgien", "Verenigde Staten": "Vereinigte Staaten", "Duitsland": "Deutschland", "Italië": "Italien", "Spanje": "Spanien", "Canada": "Kanada", "Frankrijk": "Frankreich", "Nederland": "Niederlande", "Polen": "Polen", "Tsjechië": "Tschechien", "Zweden": "Schweden", "Oekraïne": "Ukraine", "Portugal": "Portugal", "Oostenrijk": "Österreich", "Noorwegen": "Norwegen", "Zwitserland": "Schweiz", "Denemarken": "Dänemark", "Engeland": "England", "Estland": "Estland", "Ierland": "Irland"}
                try:
                    translated_value = translation_dict[value]
                except KeyError: #key not found, do not translate (or use google trans in future?)
                    translated_value = value
            if key == 'rijpingsmethode':
                translation_dict = {"Barrel Aged": "Im Fass gereift", "Niet Barrel Aged": "nicht im Fass gereift"}
                try:
                    translated_value = translation_dict[value]
                except KeyError:  # key not found, do not translate (or use google trans in future?)
                    translated_value = value
            if key == 'soort_bier':
                translation_dict = {"Barley wine": "Gerstenwein", "Blond": "Blond", "Dubbel": "Dubbel", "Tripel": "Tripel", "Saison Ale": "Saison Ale", "Lambiek/Geuze": "Lambiek/Geuze","Porter": "Porter", "Quadrupel": "Quadrupel", "Stout": "Stout", "Sour": "Sour"}
                try:
                    translated_value = translation_dict[value]
                except KeyError: #key not found, do not translate (or use google trans in future?)
                    translated_value = value

        return translated_value