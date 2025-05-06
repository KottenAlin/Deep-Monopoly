# Deep-Monopoly: Reinforcement Learning för Optimala Monopolstrategier

## Sammanfattning

Deep-Monopoly är ett projekt som utforskar hur maskininlärning kan användas för att utveckla bra spelstrategier för Monopol. Projektet kombinerar traditionell programmering med reinforcement learning för att skapa en AI som kan lära sig spela Monopol.

## Bakgrund och mål

Inspirerat av framgångar med AI i spel som schack och Go, ville vi utveckla en AI för Monopol - ett spel som är utmanande med sina slumpelement, dold information och långsiktiga strategier. Vi planerade först att använda Deep Q-Learning och Monte Carlo Tree Search (MCTS), men fokuserade till slut på vanlig reinforcement learning.

## Metod

### Spelutveckling

1. **Grunden**: Byggde först ett enkelt textbaserat Monopolspel med bra kodstruktur
2. **Funktioner**: Lade till husbyggande, auktioner, fastighetshandel och inteckning
3. **Regelbaserade bottar**: Skapade bottar med förprogrammerade strategier
4. **Statistik**: Förbättrade gränssnittet och lade till statistik för vinster och förluster

### AI-implementation

1. **Neural Bot**: Skapade en AI-agent med PyTorch
2. **Tillståndsrepresentation**: Skapade input till neuralnätet med information om spelarposition, pengar och fastigheter
3. **Aktionsrepresentation**: Designade output-lager för beslut som fastighetsköp och husbyggande
4. **Träningsmetoder**: Använde:
   - Träning mot regelbaserade bottar
   - Självspelande turneringar
   - Replay buffer för att lära från tidigare spel
5. **Belöningsfunktion**: Designade belöningar baserade på:
   - Pengar
   - Fastigheter
   - Monopolbildning
   - Vinstchanser

## Resultat

Monopol-spelet är nu fullt fungerande med en AI-agent som kan spela mot både andra AI-bottar och mänskliga spelare. Vi har också implementerat en belöningsfunktion som ger feedback till agenten baserat på spelets utfall.
AI:n kan spela mot både regelbaserade bottar och andra AI-bottar. Vi har också implementerat en replay buffer för att lagra tidigare spel och använda dem för träning.

Tekniskt fungerar allt, men träningsresultaten är inte optimala. AI-bottar kan spela mot regelbaserade motståndare men visar begränsad strategi. Belöningsfunktionen har svårt att koppla tidiga beslut till slutresultat. Även om loss-funktionen minskar, är det svårt att se tydlig förbättring i spelet.

## Upptäckta Monopolstrategier

Vi hittade flera bra strategier för Monopol:

1. **Husstrategi**:

   - Skaffa tre hus snabbt (hyra över 500 ger motståndare problem)
   - Billigare fastighetsgrupper ger snabbare vinst
   - Blå och bruna fastigheter kräver bara två fastigheter för monopol

2. **Ekonomisk strategi**:

   - Kontanter är viktigare än enstaka fastigheter utan monopol
   - Inteckna fastigheter vid behov, men sälj aldrig redan byggda hus
   - Håll alltid tillräckligt med pengar för att betala höga hyror

3. **Handelsstrategier**:

   - Byt strategiskt där motståndare får två monopol men du får ett bättre
   - Hindra andra från att bilda monopol genom "defensiv handel"
   - Spara pengar för auktioner när andra har lite pengar

4. **Taktik**:
   - Tågstationer är bara värdefulla om du har tre eller fyra
   - El- och vattenverken ger sällan bra avkastning
   - Köp hus när motståndare närmar sig dina fastigheter
   - Fängelse är bra i slutet av spelet när hyrorna är höga
   - Håll koll på vilka chans- och allmänningskort som använts

## Utmaningar

- **Fördröjd belöning**: Lång tid mellan beslut och konsekvenser i Monopol
- **Komplexitet**: Spelets många möjliga lägen gör utforskning svår
- **Slumpelement**: Tärningskast och kort skapar oförutsägbarhet
- **Prestanda**: Spelets komplexitet begränsar hur mycket träning som är möjlig

## Utvecklingspotential

1. **Bättre träningsmetoder**:
   - Längre träningstid
   - Använda Monte Carlo Tree Search
   - Stegvis ökande svårighetsgrad i träningen
2. **Bättre belöningar**:
   - Belöning baserad på vinst istället för tillstånd
   - Lära från mänskliga spelare
3. **Tekniska förbättringar**:
   - ELO-system för att ranka bottar
   - Prestandaförbättringar
   - Parallell träning
4. **Bättre utvärdering**:
   - Mer testning mot olika motståndare
   - Analys av specifika strategier

## Slutsats

Deep-Monopoly visar utmaningarna med att använda reinforcement learning för komplexa spel med slumpelement. Trots begränsade resultat ger projektet värdefulla insikter om hur man kan modellera Monopol för maskininlärning och skapar grund för framtida förbättringar.

![Träningsresultat](assets/training_progress.png)
