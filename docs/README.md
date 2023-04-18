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

Om een gefinetuned model voor zowel Curie als Davinci te realiseren waren de ESPN wedstrijdsamenvattingen (web scraped) van essentieel belang. Aangezien er twee 'Main components' nodig zijn om een eigen model te trainen: </br>
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
Om iedereen te laten testen met het Language model met diverse wedstrijden, is er een applicatie gebouwd in Streamlit. De applicatie is opgebouwd met het Streamlit multipage principe. Bestaande uit 3 pagina's: </br>
1. **Home page**: Introductie pagina van de Web App. </br>
2. **Genereer Samenvatting page**: Hier kan men met diverse wedstrijden testen en zelf diverse prompts creeëren door middel van de fijne User Interface. </br>
3. **Analyse Page**: Hier zijn diverse insights te vinden over de data die is gebruikt (Eredivisie). </br>

### Home page
De home pagina is puur ter introductie van de Applicatie, niets meer en minder.
### Genereer samenvatting page
#### Security
Deze pagina is beveiligd door middel van een gebruikersnaam en wachtwoord. </br>
De reden hiervoor is dat onbevoegde mensen dan niet zomaar gebruik kunnen maken van de OpenAI API key van Southfields. Dit voorkomt random kosten/verbuik in API calls. </br>

#### Parameters 
Nadat je succesvol bent geautoriseerd heb je toegang tot de officiele 'genereer samenvatting page'. </br>
Op deze pagina is het mogelijk om in de **sidebar** het model te selecteren (*gpt-3.5-turbo geadviseerd*). Daarnaast is het mogelijk om twee model parameters te veranderen: </br>
- **Maximum Tokens**: Maximum of characters/tokens in the output (1000 tokens is about 750 words)</br>
- **Model Temperature**: Creation of randomness (Higher value) or make the model more focused (Lower value).</br>
<img src="assets/model_parameters.png" width="25%" height="25%"/>

In het 'hoofd gedeelte' van de pagina kan je een selectie doen op: </br>
- Wedstrijd datum </br>
- Wedstrijd die op de geselecteerde datum heeft plaats gevonden </br>

Meenemen in de prompt ja/nee: 
- De blessures van het **thuis** team (Op basis van de twee bovenstaande geselecteerde velden) </br>
- De blessures van het **uit** team (Op basis van de twee bovenstaande geselecteerde velden) </br>
- De trainersnamen </br>
<img src="assets/other_preferences.png" width="70%" height="70%"/>

#### Genereer Samenvatting
Het textveld veranderd interactief, door de handelingen van de user. Zo word er dus voor elke wedstrijd een unieke prompt gecreeërd in het textveld onder 'Wedstrijd data'. </br>
In de background wordt alle OPTA data van de geselecteerde wedstrijd opgehaald en geprocessed in een 'natural language' format, dit process word ook wel een pipeline genoemd. </br>
Het is zelfs ook nog mogelijk om in het textveld handmatig extra data/text mee te geven als input voor het model. </br>
Zodra de user de gewenste prompt voor zich heeft, hoeft de user enkel de '**Genereer**' button te activeren. </br>
<img src="assets/example_generate.gif" width="80%" height="80%"/>

### Analyse page
Op deze pagina is het mogelijk om analyse uit te voeren door middel van interactieve plots. </br>
Voor nu is het enkel gebaseerd op Eredivisie data, en is het puur ter illustratie en geneert het interessante user insights. </br>
<img src="assets/words_SF.png" width="45%" height="45%"/>
<img src="assets/trigrams_SF.png" width="47.5%" height="51%"/>

