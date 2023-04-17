# Introductie - Project GPT3 - GPT3.5
*Author: Marc Blomvliet - Aurai* </br>
Dit project is gestart als MVP.
Het doel van het project is om middels van play by play data, afkomstig van OPTA, Voetbal wedstrijdsamenvattingen te genereren.

## Bouwstenen
Om een beter beeld te krijgen hoe de GIT Repository is opgebouwd, verdeel ik het in hoofdzakelijk 4 componenten. </br>
- ESPN Scraper om Wedstrijd samenvattingen te vergaren */espn_scraper*
- OPTA Data (API) - Data to prompt Pipeline */opta*
- OpenAI GPT3 Trainings Pipeline */openai_GPT3*
- Streamlit Web Application */pages* + */.streamlit* + File *Home.py*

Om een gefinetuned model voor zowel Curie als Davinci te realiseren waren de gescrapede ESPN wedstrijdsamenvattingen van essentieel belang. Aangezien er twee 'Main components' nodig zijn om een eigen model te trainen: </br>
1. Play by Play data (OPTA) als input (Prompt), dit wordt gebruikt als input voor het model om te kunnen begrijpen wat het nodig heeft om een wedstrijdsamenvatting te kunnen schrijven.  </br>
2. Historische wedstrijdsamenvattingen (Completion), dit wordt gebruikt zodat het model begrijpt wat het ongeveer moet gaan genereren/schrijven aan de hand van de Input data. </br>

Er is een pipeline gebouwd om alle benodigde/gewenste data uit OPTA op te halen en uiteindelijk te engineeren tot een **perfecte** Prompt (Input voor het ML model). </br>
*Belangrijk is om een natuurlijk geschreven prompt aan te leveren aan het model, om een zo goed mogelijke completion(resultaat) terug te krijgen.* </br>
Met een "natuurlijk geschreven prompt" wordt bedoeld, dat de ruwe data moet worden vertaald naar "natural language". Dit is gerealiseerd door middel van een pipeline script (geschreven in Python). </br>
Een voorbeeld hiervan is: </br>
> prompt ruwe data (Foutief): {helft=1, minuut=3, type=G, speler=Córdoba} </br>
> prompt natural language (Goed): {Córdoba scoorde voor Fortuna Sittard in de 1e helft in minuut 3} </br>

Ten derde is er een Trainings pipeline gebouwd, dit is het process wat na de OPTA pipeline komt. Dus zodra alle OPTA data opgehaald, geprocessed en weggeschreven is naar een *.csv* file. </br>
De trainings pipeline creeert het juiste format wat gewenst is vanuit OpenAI, enkel twee columns/keys: prompt en completion.
De trainings pipeline engineert alle OPTA data wat is opgehaald tot een vlot en begrijpbaar verhaal. En daarnaast zorgt het er ook voor dat alle events in de juiste tijdlijn achter elkaar staan, wat uiteindelijk weer de kans verhoogd voor een goed lopend en een correcte wedstrijdsamenvatting. </br>

Om iedereen te laten testen met het Language model met diverse wedstrijden, is er een applicatie gebouwd in Streamlit. De applicatie bestaat uit 3 pagina's.

**De volgende hoofdstukken zullen dieper ingaan op deze bouwstenen van de Git Repository.**

# ESPN Website Scraper 
De wedstrijd samenvattingen van ESPN staan niet in een grijpbare Database van bijvoorbeeld een cloudprovider zoals: AWS, Azure of GCloud. Daarom is er een webscraper gebouwd om alle Eredivisie en Keuken kampioen divisie wedstrijdsamenvattingen op te halen.

# OPTA (API) Interaction

# Streamlit Application
**Introductie Streamlit:** </br>
Voor dit project heb ik gebruik gemaakt van Streamlit, een open-source Python library. 
Het is erg gebruiksvriendelijk voor zowel de user als de developer. Het is fijn in gebruik om snel een 'fancy' maar met name 'praktische' custom  web applicatie mee te bouwen. Zelf vind ik het erg fijn om te gebruiken voor machine learning demos/toepassingen.

## Constructie
Om iedereen te laten testen met het Language model met diverse wedstrijden, is er een applicatie gebouwd in Streamlit. De applicatie bestaat uit 3 pagina's: </br>
1. **Home page**: Introductie pagina van de Web App. </br>
2. **Genereer Samenvatting page**: Hier kan men met diverse wedstrijden testen en zelf diverse prompts creeëren door middel van de fijne User Interface. </br>
3. **Analyse Page**: Hier zijn diverse insights te vinden over de data die is gebruikt (Eredivisie). </br>

### Home page

### Genereer samenvatting page

### Analyse page