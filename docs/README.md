# Presentation: Meet TEDDY
Link: [Meet Teddy](https://spark.adobe.com/page/BcSAFWkIpK2id/) (Adobe Spark)

# Presentation: TEDDY 2.0 Features & Updates
Link: [Teddy 2.0](https://spark.adobe.com/page/SPBxNf1anb9Y7/) (Adobe Spark)

<a class="asp-embed-link" href="https://spark.adobe.com/page/BcSAFWkIpK2id/" target="_blank"><img src="https://spark.adobe.com/page/BcSAFWkIpK2id/embed.jpg?buster=1626383713887" alt="Meet TEDDY" style="width:80%; align:center" border="0" /></a>

<a class="asp-embed-link" href="https://spark.adobe.com/page/SPBxNf1anb9Y7/" target="_blank"><img src="https://spark.adobe.com/page/SPBxNf1anb9Y7/embed.jpg?buster=1628267959506" alt="TEDDY v2.0" style="width:100%" border="0" /></a>

# The Functions:

- Basic Search
  - In:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/teddy-command.png">
  - Out:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/BasicOutput.png?raw">
- Search With Basic Filters
  - Choices: 
    - `region:` (NA, SA, SE, EU, All-Regions (default)
    - `mode:` (Classic, Brawl, Rank, All-Modes (default))
    - `elo:` (Normal, High, Very-High, All-Levels(default))
    - `period:` (All-Time, Month, Week (default))
    - `sort:` (see below)
    - `role:` (see below)  
  - In:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/BasicFilters-Command.png?raw=true">
  - Out:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/BasicFilters.png?raw=true">
- Sort
  - Choices: `Top (default), Bottom`  
  - In:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/BasicSort.png?raw=true">
  - Out:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/Sort-Bottom.png?raw=true">
- Role
  - Choices: `Assassin, Marksman, Tank, Mage, Support, Fighter, None (default)`
  - In:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/BasicRole.png?raw=true">
  - Out:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/Filter-Mage.png?raw=true">
- View Meta/Role
  - Choices: `Normal (default), Meta, Role` 
  - In:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/BasicView.png?raw=true">
  - Out:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/View-Meta.png?raw=true">
- About
  - Choices: `Teddy, The Data, Outliers, None (default)` 
  - In:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/BasicAbout.png?raw=true">
  - Out:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/About-Basic.png?raw=true">
## Data Flow
<img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/TEDDY%20FLOW-TEDDY-BetaRC.png">

# DEV Functions
Repository: [MLBB-TeddyBot-DEV](https://github.com/p3hndrx/MLBB-TeddyBot-DEV)
- Search by Hero<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/Hero-Basic-Command.png?raw=true">
  - hero: `Your Hero Input` (can match partial strings) 
  - Choices: 
    - `region:` (NA, SA, SE, EU, All-Regions (default)
    - `mode:` (Classic, Brawl, Rank, All-Modes (default))
    - `elo:` (Normal, High, Very-High, All-Levels(default))
    - `period:` (All-Time, Month, Week (default))
    - `Show:` (see below)
  - In:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/Hero-Command.png?raw=true">
  - Out:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/Hero-Basic.png?raw=true">
- Optional: Hero: History View
  - Choices: `History, None (default)` 
  - In:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/Hero-History-Command.png?raw=true">
  - Out:<br><img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/Hero-Timeline.png?raw=true">

## DEV Data Flow
<img src="https://github.com/p3hndrx/MLBB-TeddyBot/blob/main/docs/img/TEDDY%20FLOW-TEDDY-DEV.png?raw=true">
