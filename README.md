# Model pościgowy
## Projekt z przedmiotu "Studio projektowe 1"

# Autorzy

- [Łukasz Łabuz](https://github.com/luklabuz)
- [Tomasz Kawiak](https://github.com/hevagog)
- [Mateusz Mazur](https://github.com/mzsuetam)

# Temat projektu

Tematem projektu jest stworzenie modelu pościgowego,
który będzie pozwalał na symulację zachowań 1 policjanta (goniący) i 1 przestępcy (uciekający)
w zamkniętej przestrzeni.

## Założenia projektowe

- Przestrzeń będzie zamknięta
- Przestrzeń będzie zawierała przeszkody
- Przestrzeń będzie ładowana z pliku, w celu testowania różnych konfiguracji
- Aktorzy będą w stanie poruszać się samodzielnie
- Aktorzy będą w stanie unikać przeszkód
- Aktorzy będą reagować na obecność innych aktorów (goniący będzie gonił uciekającego, a uciekający będzie uciekał przed goniącym)
- Uciekający będzie szukał wyjścia z przestrzeni (docelowego punktu)
- Goniący będzie próbował złapać (dotknąć) uciekającego
- Po zakończeniu symulacji będzie możliwa analiza danych (np. średnia prędkość, czas ucieczki, czas goniącego, itp.)

# Rozwiązanie problemu

## Środowisko symulacyjne

Symulacja została zrealizowana w języku Python, z wykorzystaniem bibliotek PyGame oraz NumPy.

Symulator został zrealizowany jako posty, dyskretny silnik fizyczny,
który symuluje ruch aktorów w przestrzeni, jako ruch punktów materialnych.
Oddziaływanie na ruch aktorów jest realizowane
poprzez zastosowanie sił, które są nakładane na punkty materialne.

Wyświetlanie przestrzeni oraz aktorów jest realizowane poprzez bibliotekę PyGame 
na podstawie stanu symulacji. GUI symulatora przedstawione jest na rysunku \ref{img:hui}

![GUI symulatora \label{img:hui}](docs/img/gui.png){width=90%}

Po zakończeniu symulacji możliwy jest eksport danych dotyczących symulowanych punktów.
Istnieje również możliwość wyświetlenia wykresów z danymi dotyczącymi symulacji
(stworzonymi na podstawie eksportowanych danych). Przykładowy wykres pozycji aktorów
przedstawiony jest na rysunku \ref{img:chart}.

![Wykres pozycji aktorów \label{img:chart}](docs/img/positions.png){width=90%}

## Model zachowań aktorów

Zachowanie aktorów realizowane jest poprzez kontrolery.
W każdym kroku czasowym symulatora, kontrolery aktorów decydują o tym, jakie siły mają zostać nałożone na aktorów.
Modelują one jednocześnie stan wiedzy aktorów, podejmowane przez nich decyzje oraz ich zachowania.

Kontrolery aktorów są zaimplementowane w taki sposób, aby były niezależne od siebie.
Dzięki temu można je dowolnie łączyć, aby uzyskać pożądane zachowanie aktora.
Na potrzeby symulacji zostały zaimplementowane m.in. następujące kontrolery:

- `astar`: kontroler, który realizuje poruszanie się w przestrzeni na bazie wyjścia z algorytmu A*,
- `forecasting`: kontroler, który realizuje przewidywanie ruchu danego aktora
- `vision`: kontroler, który realizuje poszukiwanie celu oraz ograniczenie widoczności aktora

Głównymi kontrolerami aktorów są:

- `escaping`: kontroler realizujący ucieczkę aktora, korzysta z kontrolera `astar` oraz `vision`, 
  dokładając do nich chęć ucieczki od aktora, który go goni.
- `chasing`: kontroler realizujący gonienie aktora, korzysta z kontrolera `astar` oraz `forecasting`, 
  rozszerzając jego funkcjonalność o chęć dotknięcia uciekającego aktora.
  Wykorzystaliśmy w tym przypadku macierz prawdopodobieństwa przyszłej pozycji aktora uciekającego.

# Napotkane trudności i ich rozwiązania

## Przewidywanie przez aktora goniącego pozycji aktora uciekającego

Rozwiązaniem tego problemu było zastosowanie macierzy prawdopodobieństwa przyszłej pozycji aktora uciekającego.
Macierz ta jest obliczana na podstawie prędkości poruszania się uciekającego przez kontroler `forecasting` 
z późniejszym uwzględnieniem przeszkód w przestrzeni. Inspiracją do tego rozwiązania był projekt 4: _Ghostbusters_
z kursu [UC Berkeley CS188 Intro to AI](http://ai.berkeley.edu/tracking.html).

## Wykorzystanie kontrolerów w innych kontrolerach

Pierwszym pomysłem implementacji kontrolerów było wykorzystanie dziedziczenia.
Pojawił się jednak problem, że kontrolery nie mogły być ze sobą łączone,
ponieważ ich metoda `update` była nadpisywana, a nie rozszerzana.
Wadą takiego rozwiązania jest np. aktywacji tylko w pewnych przypadkach
lub ograniczenia wartości sił zwracanych przez kontrolery.

Rozwiązaniem tego problemu było wykorzystanie kompozycji, a nie dziedziczenia 
(nie licząc kontrolerów bazowych),
oraz rozdzielenie logiki kontrolerów od faktycznego wpływu na aktora.
Dzięki takiemu rozwiązaniu kontrolery mogą być dowolnie łączone i wykorzystywać 
wyniki zwracane przez inne kontrolery.

## Optymalizacja działania kontrolerów

Aby symulacja działała poprawnie, konieczne było ciągłe zwrócenie uwagi na optymalność działania kontrolerów.

Szczególnie problematyczne okazało się przewidywanie pozycji aktora uciekającego przez aktora goniącego.
Pierwsza implementacja tego rozwiązania była bardzo kosztowna obliczeniowo,
ponieważ do sprawdzenia potencjalnych pozycji aktora uciekającego pod kątem kolizji z przeszkodami.
Dzięki zmianie sposobu obliczania z pętli zagnieżdżonych na pojedynczą pętlę po przefiltrowanych pozycjach 
udało się 100-krotnie zmniejszyć czas obliczeń tego elementu.

# Podział prac

- Łukasz Łabuz
  - stworzenie kontrolera przewidywania
  - stworzenie kontrolera gonienia
- Tomasz Kawiak
  - stworzenie kontrolera widzenia
  - stworzenie kontrolera ucieczki
- Mateusz Mazur
  - stworzenie silnika symulacyjnego
  - optymalizacja działania kontrolerów gonienia i ucieczki
