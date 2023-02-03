# Energy-Data-Scrapping

Celem tego projektu bylo pobranie danych z 3 stron:

https://www.pse.pl/dane-systemowe/funkcjonowanie-kse/raporty-dobowe-z-pracy-kse/generacja-mocy-jednostek-wytworczych

https://www.pse.pl/dane-systemowe/funkcjonowanie-kse/raporty-dobowe-z-pracy-kse/wielkosci-podstawowe

https://tge.pl/energia-elektryczna-rdn

a nastepnie wygenerowanie raportu wybranego przez uzytkownika dla zadanego okresu czasu.

## Instrukcja obslugi dla użytkownika:

### 1. Wybierz jedną z opcji wpisujac na klawiaturze 1/2/3/4 lub jakikolwiek inna wartosc:
1. Generuj raport: Praca KSE- Generacja mocy Jednostek Wytwórczych
2. Generuj raport: Praca KSE - wielkości podstawowe
3. Generuj raport: TGE - Kontrakty Godzinowe
4 lub jakikolwiek inny input: Zakończ

Generowanie raportu moze zajac dluzsza chwile ze wzgledu na to ze generowanie danych przez strony zajmuje pewnien czas 
i nie jest to zwiazane z dzialaniem programu. Dla raportu 1. Generacja mocy JW strona KSE generuje dane okolo 3 min dla okresu 1 miesiąca. Dlatego pobierając dane dla np 3 miesięcy czas oczekiwanie na dane będzie równy do 10 minut. Im szerszy zakres dat wybierze uzytkownik tym dluzszy czas oczekiwania

Raport RGE - Kontrakty Godzinowe moze zawierac dane tylko 2 miesiace wstecz, poniewaz tylko taki zakres danych jest dostepny na stronie TGE

### 2. Wybierz lokalizację gdzie chcesz zapisać raport
wpisz ścieżke lokalizacji w ktorej chcesz zapisac raport np: C:\Users\Public\Documents

### 3. Podaj daty poczatkowe i koncowe zgodne z formatem YYYY-MM-DD. Niepoprawny format spowoduje zapytanie programu o ponownie wprowadzenie dat

### 4. Poczekaj az program skonczy prace, natepnie raport bedzie dostepny w postaci .xlsx w lokalizacji ktora podal uzytkownik
