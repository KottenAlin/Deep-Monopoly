# Deep-Monopoly: AI som lär sig spela Monopol med MCTS och Deep Q-Learning

## Projektöversikt
Deep-Monopoly är ett projekt som syftar till att utveckla AI-agenter som kan lära sig spela brädspelet Monopol genom en hybridmetod som kombinerar Monte Carlo Tree Search (MCTS) och Deep Q-Learning. Projektet undersöker hur dessa tekniker presterar i jämförelse med mänskliga spelare, inspirerat av framgången med AlphaGo inom schack och Go.

## Utmaningar
Monopol presenterar flera unika utmaningar för AI:
- Långsiktig strategisk planering (spel kan pågå hundratals rundor)
- Stokastiska element (tärningskast, kort)
- Ofullständig information (andra spelares strategier)
- Kombinatorisk komplexitet (fastighetsköp, byten, utveckling)
- Fördröjda belöningar (tidiga beslut påverkar slutskedet)

## Mål
- Utveckla AI-modeller som kan spela Monopol på en konkurrenskraftig nivå
- Implementera och optimera en hybrid av MCTS och djup förstärkningsinlärning
- Analysera strategier som AI:n utvecklar och om dessa kan vara användbara för mänskliga spelare
- Skapa en plattform där människor kan spela mot och lära sig från AI-agenterna

## Teknisk approach
### Teknisk approach

#### Neurala nätverksarkitekturen
Vi använder ett neuralt nätverk med två huvudfunktioner:
1. **Värdefunktionen**: Bedömer hur bra spelets nuvarande position är
2. **Policykomponenten**: Hjälper AI:n välja nästa drag

Nätverket har en struktur med:
- Indata: Information om spelets nuvarande situation
- Flera interna lager som bearbetar informationen
- Två separata utgångar som ger värderingar och beslutsförslag

#### Hybrid algoritm för förstärkt inlärning
- **Monte Carlo Tree Search (MCTS)**:
    - Hjälper AI:n planera framåt genom att utforska möjliga spelvägar
    - Balanserar mellan att prova nya strategier och använda beprövade taktiker
    - Anpassar sig till Monopols slumpmässiga natur

- **Deep Q-Learning (DQN) med förbättringar**:
    - Lagrar och lär sig från tidigare spelerfarenheter
    - Använder flera tekniker för att undvika vanliga inlärningsproblem
    - Förbättrar förmågan att koppla tidiga beslut till slutresultat

- **Träningsalgoritm**:
    - AI:n spelar mot sig själv för att generera träningsdata
    - Nätverket förbättras kontinuerligt baserat på spelresultat
    - Inlärningen börjar med enklare versioner av spelet och ökar i komplexitet

## Implementering
### Utvecklingsplan
1. **Fas 1**: Grundläggande speluppbyggnad
    - Skapa en enkel version av Monopol i Python
    - Förbereda spelet för att kunna kommunicera med AI
    - Utveckla hur speltillstånd och möjliga handlingar representeras

2. **Fas 2**: Utveckling av AI-hjärnan
    - Designa och bygga det neurala nätverket 
    - Skapa system för att träna nätverket
    - Utveckla sätt att mäta hur bra AI:n presterar

3. **Fas 3**: Strategisk planering med MCTS
    - Bygga algoritmen som hjälper AI:n att tänka framåt
    - Koppla ihop planering med det neurala nätverket
    - Anpassa för Monopols slumpmässiga natur (tärningar, kort)

4. **Fas 4**: Förstärkt inlärning med DQN
    - Skapa system för AI:n att lära sig från tidigare erfarenheter
    - Utveckla mekanismer för att förbättra beslut över tid
    - Kombinera med framåtblickande planering

5. **Fas 5**: Träning och förbättring
    - Låta AI:n spela mot sig själv för att bli bättre
    - Finjustera inställningar för bästa resultat
    - Utvärdera prestanda mot andra spelare


## Inlärningsprocess
### Träningsloop
1. **Initialisera**: Slumpmässiga nätverksvikter
2. **Generera data**: Använd nuvarande nätverk med MCTS för att spela spel
3. **Lär**: Uppdatera nätverket baserat på spelresultat
4. **Utvärdera**: Testa mot tidigare versioner
5. **Upprepa**: Med förbättrat nätverk

### Curriculum Learning
- Börja med förenklad version av Monopol
- Gradvis öka komplexitet med fullständiga regler
- Öka MCTS-simulationsdjupet över tid
- Skala upp neurala nätverkskomplexitet

## Hantering av slumpmässighet
- **Förväntade värdeberäkningar**: Inkorporera tärningskastsannolikheter
- **Multipla simuleringar**: Genomsnittliga resultat över många möjliga tärningssekvenser
- **Riskjusterade utvärderingar**: Beakta variansen av utfall
- **Landningssannolikhetsfördelningar** för olika brädpositioner
- **Fängelsestrategi-optimering**

## Utvärderingsramverk
- Vinstgrad mot regelbaserade AI-motståndare
- Vinstgrad mot tidigare versioner
- Beslutskvalitetsanalys
- Strategisk diversitetsmätning
- Visualisering av speltillstånd
- Beslutsförklaringsförmåga

## Framtida möjligheter
- Multi-agent reinforcement learning för mer spelarinteraktion
- Meta-learning för anpassning till olika spelstilar
- Inlärning fårn mäsnklig demonstration
- Explainable AI-komponenter för strategiska insikter
- Webbaserat gränssnitt där allmänheten kan spela mot AI:n

## Inspiration
Projektet inspireras av liknande arbete inom andra speldomäner, specifikt [AI Learns Insane Monopoly Strategies](https://www.youtube.com/watch?v=dkvFcYBznPI), där genetiska algoritmer används, samt framgången med hybridmetoder som i AlphaGo och AlphaZero.

## Resultat

## Reflektion