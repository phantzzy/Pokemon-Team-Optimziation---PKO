# Pokémon aizsardzības komandas optimizācija ar imitēto atkvēlināšanu

**Kurss:** Praktiskā kombinatoriskā optimizācija<br>
**Repozitorijs:** https://github.com/phantzzy/Pokemon-Team-Optimziation---PKO<br>
**Students:** Raivis Randohs<br>
**Datums:** 2026. gada 11. oktobris

> Tālāk norādītie 30 izpildes reižu etalonmērījumu rezultāti tika iegūti
> 2026. gada 11. oktobrī. Pirms iesniegšanas studentam vēl jāpārskata rezultāti.

## 1. Problēmas formulējums

Uzdevums ir no fiksētas N kandidātu kopas izvēlēties komandu ar tieši sešiem
unikāliem Pokémon. Modelī tiek vērtēti tikai aizsardzības tipi. Gājieni,
statistikas rādītāji, spējas, priekšmeti, EV, IV, Tera tipi, lietojuma dati un
cīņas simulācija netiek ņemti vērā.

Ar P apzīmē kandidātu kopu, bet ar T - risinājumu. Derīgs risinājums ir
nesakārtota sešu elementu P apakškopa. Tādēļ iespējamo risinājumu skaits ir
C(N, 6). Tas pieaug no 924 komandām, ja N=12, līdz 1 192 052 400 komandām,
ja N=100, tāpēc lielākām problēmas instancēm ir nepieciešama metaheiristika.

Uzbrūkošajam tipam t un Pokémon p ar m(t,p) apzīmē standarta tipa efektivitātes
reizinātāju aizsardzībā. Vienam aizsardzības tipam reizinātājs ir 0, 0,5, 1 vai
2. Divu tipu Pokémon gadījumā abu aizsardzības tipu reizinātājus sareizina,
tāpēc gala vērtība var būt arī 0,25 vai 4.

Komandas izmaksu funkcija ir:

    f(T) = summa visiem p no T un visiem uzbrukuma tipiem t: m(t,p)

Mērķis ir minimizēt f(T). Mazāka vērtība nozīmē vidēji labāku aizsardzības tipu
kombināciju. Rezultātu interpretācijai programma norāda arī:

    VidējaisReizinātājs = f(T) / 108

jo seši Pokémon tiek vērtēti pret visiem 18 uzbrukuma tipiem.

## 2. Izstrādātais risinājums

### a) Risinājumu apgabals

Risinājumu attēlo seši unikāli Pokémon no aktīvās instances. Piecās fiksētās
instancēs ir attiecīgi 12, 20, 30, 50 un 100 kandidāti. Iespējamo komandu skaits
ir 924; 38 760; 593 775; 15 890 700 un 1 192 052 400. Programma pārbauda
kandidātu piederību instancei, komandas izmēru un elementu unikalitāti.

Lokālajā datu kopā ir 100 sugas un pilna 18 reiz 18 tipu tabula, kas iegūta no
PokéAPI. Pirms optimizācijas katram Pokémon tiek aprēķināts 18 aizsardzības
reizinātāju vektors. Tādēļ meklēšanas ciklā nav nepieciešama failu vai tipu
tabulas nolasīšana.

### b) Novērtēšana

Novērtēšanas funkcija saskaita sešus iepriekš aprēķinātos aizsardzības
vektorus. Tā ir deterministiska un nav atkarīga no komandas elementu secības.
Optimizētājs tieši minimizē neapstrādāto izmaksu vērtību; vidējais reizinātājs
tiek izmantots tikai rezultātu attēlošanai.

Šis kritērijs apzināti vērtē tikai individuālo aizsardzības tipu kombināciju.
Tas nemodelē lomas, uzbrukuma tipu pārklājumu vai cīņas sinerģiju, tādēļ
uzdevums ir matemātiski skaidrs un reproducējams.

### c) Gājiens un apkārtne

Kaimiņrisinājumu iegūst ar viena elementa maiņu:

1. nejauši izvēlas vienu pašreizējās komandas dalībnieku;
2. nejauši izvēlas vienu kandidātu, kas nav pašreizējā komandā;
3. pirmo aizstāj ar otro.

Gājiens vienmēr rada derīgu sešu elementu komandu bez dublikātiem. Visām
nejaušajām izvēlēm izmanto lokālu nejaušo skaitļu ģeneratoru ar noteiktu
sēklas vērtību.

### d) Algoritms

Imitētās atkvēlināšanas (SA) algoritms ir izstrādāts manuāli, neizmantojot
optimizācijas bibliotēku. Algoritms sāk darbu ar nejaušu derīgu komandu un to
saglabā gan kā pašreizējo, gan kā labāko risinājumu. Katrā iterācijā izveido
vienu kaimiņrisinājumu un aprēķina delta kā kandidāta un pašreizējā risinājuma
izmaksu starpību.

Ja delta ir nulle vai negatīva, kandidāts tiek pieņemts. Ja delta ir pozitīva,
to pieņem ar varbūtību exp(-delta / temperatūra). Tas meklēšanas sākumā ļauj
atkāpties no lokāla optimuma. Pēc katras iterācijas temperatūru reizina ar
alpha. Izpilde beidzas, sasniedzot iterāciju ierobežojumu vai temperatūrai
nokrītot zem minimālās vērtības. Visā izpildes laikā atrastais labākais
risinājums tiek atgriezts atsevišķi no pēdējā pašreizējā risinājuma.

Noklusētie parametri ir sākuma temperatūra 10,0, alpha 0,995, minimālā
temperatūra 0,0001 un ne vairāk kā 20 000 iterāciju. Ar noklusēto dzesēšanas
grafiku temperatūras nosacījums izpildi aptur pēc 2297 iterācijām. Vienāda
instance, sēkla un parametri reproducē vienādu komandu un izmaksu vērtību.

Atsevišķs precīzais risinātājs mazām instancēm pārbauda visas C(N, 6)
kombinācijas. Tas pierāda salīdzināšanai izmantoto optimumu, bet nav galvenais
optimizācijas algoritms.

## 3. Testēšanas process un rezultāti

Projektā ir 48 automatizēti vienību un integrācijas testi. Tie pārbauda zināmas
viena un divu tipu mijiedarbības, datu validāciju, izmaksu determinismu,
apkārtnes invariantus, algoritma derīgumu un reproducējamību, apstāšanās
nosacījumus, precīzā risinātāja korektumu, komandrindas saskarni, fiksētās
instances, novirzes aprēķinus un CSV izvadi. Visi testi sekmīgi izpildīti ar
Python 3.11.9.

Etalonmērījumos imitētās atkvēlināšanas algoritms katrai instancei tika
izpildīts 30 reizes ar sēklām no 0 līdz 29. Katrai izpildei saglabāja izmaksas,
vidējo reizinātāju, izpildes laiku, sēklu, komandu un novirzi. Instancēm līdz
N=30 novirze tika aprēķināta pret pierādīto optimumu:

    Novirze(%) = (SA - OPT) / OPT * 100

Ja N=50 un N=100, precīzā pilnā pārlase netika veikta. Mazākā no 30 algoritma
izpildēs iegūtajām izmaksām tiek apzīmēta kā labākā zināmā, nevis optimālā
vērtība.

Precīzais risinātājs ir pārbaudījis šādas izmaksas:

| Instance | N | Iespējamās komandas | Pierādītais optimums |
|---|---:|---:|---:|
| small_12 | 12 | 924 | 108,75 |
| medium_20 | 20 | 38 760 | 104,50 |
| medium_30 | 30 | 593 775 | 103,50 |

| Instance | Atsauces vērtība | Labākā | Vidējā | Sliktākā | Vidējā novirze | Vidējais laiks |
|---|---:|---:|---:|---:|---:|---:|
| small_12 | 108,75 optimāla | 108,75 | 108,75 | 108,75 | 0,0000% | 9,418 ms |
| medium_20 | 104,50 optimāla | 104,50 | 104,50 | 104,50 | 0,0000% | 11,242 ms |
| medium_30 | 103,50 optimāla | 103,50 | 103,50 | 103,50 | 0,0000% | 12,652 ms |
| large_50 | 101,75 labākā zināmā | 101,75 | 101,75 | 101,75 | 0,0000% | 14,534 ms |
| xlarge_100 | 93,75 labākā zināmā | 93,75 | 93,75 | 93,75 | 0,0000% | 24,019 ms |

Visās 30 izpildes reizēs algoritms sasniedza pierādīto optimumu katrai
instancei ar 12, 20 un 30 kandidātiem. Tādēļ labākā, vidējā un sliktākā
novirze bija nulle. Arī N=50 un N=100 gadījumā visas izpildes atgrieza vienādu
izmaksu vērtību. Šīs vērtības tomēr ir tikai labākās zināmās, jo šāda izmēra
instancēm pilnā pārlase netika veikta. Vidējais izpildes laiks pieauga no
9,418 ms, ja N=12, līdz 24,019 ms, ja N=100, saglabājoties piemērots
interaktīvai lietošanai. Rezultātu stabilitāte ir ticama šim apzināti
vienkāršajam aditīvajam aizsardzības izmaksu modelim, tomēr tā nepierāda abu
lielo instanču globālo optimalitāti.

## 4. Secinājumi

Projekts demonstrē pilnu kombinatoriskās optimizācijas darba procesu: precīzu
risinājumu apgabala definīciju, deterministisku mērķfunkciju, derīgumu
saglabājošu apkārtni, manuāli izstrādātu imitētās atkvēlināšanas algoritmu,
precīzu pārbaudi mazām instancēm, reproducējamus eksperimentus un CSV
rezultātu saglabāšanu. Realizācija stabili atrada visus zināmos mazo instanču
optimumus un ieguva stabilus labākos zināmos rezultātus daudz lielākām
meklēšanas telpām.
