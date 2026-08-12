# Projekt pokoju

Narzędzia do zaprojektowania nowego układu pokoju: rzut w skali, automatyczna
kontrola ergonomii, porównanie wariantów.

## Stan

Dane w `room.json` są **zastępcze** (`meta.status: "PLACEHOLDER"`) — wymiary są
zmyślone, żeby narzędzie dało się uruchomić i przetestować. Realne pomiary
zbierane są przez [BRIEF.md](BRIEF.md).

## Pliki

| Plik | Rola |
|---|---|
| `room.json` | Jedyne źródło prawdy: wymiary pokoju, okno, drzwi, grzejnik, gniazdka, meble, warianty układu |
| `template.html` | Szablon strony — rysowanie SVG i cała analiza |
| `build_plan.py` | Waliduje `room.json` i wstrzykuje go do szablonu |
| `plan.html` | **Wygenerowany** — nie edytuj ręcznie |
| `BRIEF.md` | Formularz na dane wejściowe |

## Użycie

```bash
python3 room-design/build_plan.py
```

Skrypt najpierw waliduje dane i przerywa z listą błędów, jeśli np. mebel jest
użyty dwa razy w jednym układzie, okno wychodzi poza ścianę albo jakiś mebel
nie został rozstawiony.

## Układ współrzędnych

Origin `(0,0)` = narożnik północno-zachodni. `x` rośnie na wschód, `y` na
południe. Ściany: `N` = y0, `S` = y max, `W` = x0, `E` = x max.

- `offset` w otworach i osprzęcie — odległość wzdłuż ściany od narożnika N (dla ścian W/E) lub W (dla ścian N/S)
- `placements[].x/y` — **środek** mebla, nie narożnik
- `rot` — 0 lub 90 stopni (wielokrotności 90)

Wszystko w centymetrach.

## Co strona liczy sama

Kontrola ergonomii nie jest wpisana ręcznie — wynika z geometrii:

- **kolizje** mebli między sobą i z obrysem pokoju
- **grzejnik** zasłonięty meblem
- **łuk otwierania drzwi** — sektor kołowy o promieniu równym szerokości skrzydła; mebel w tym sektorze blokuje drzwi
- **najwęższe przejście** — transformata odległości na siatce 5 cm, potem BFS od drzwi dla osoby przyjętej jako okrąg. Zwiększany jest promień, aż przestaje dać się dojść do wszystkich mebli; ostatni działający promień × 2 = szerokość najwęższego gardła na trasie
- **dostęp do łóżka** z boku i **miejsce przed szafą** na otwarcie drzwi
- **zasięg do gniazdka** dla mebli z `needsPower: true`
- **strefa hobby** — czy zadeklarowana wolna podłoga faktycznie jest wolna

Progi siedzą w `room.json` → `rules`, więc da się je zmienić bez ruszania kodu.

Uwaga projektowa: łuk drzwi blokuje **stawianie mebli**, ale nie blokuje
**chodzenia** — przez otwarte drzwi się przechodzi. Te dwie rzeczy są liczone
osobno.

## Dalsze kroki

1. Podmienić `room.json` na realne pomiary z `BRIEF.md`, ustawić `meta.status` na `"REAL"`
2. Odtworzyć układ `PRZED` ze zdjęć
3. Dopracować warianty, wybrać jeden
4. Kierunki stylistyczne → rendery
5. Lista zakupowa do 2000 zł
