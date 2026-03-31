import os

# Dane zaktualizowane na podstawie tabeli ze zdjęcia
# Format: "Nazwa": (Liczba_miast, Optymalny_koszt)
atsp_solutions = {
    "br17": (17, 39),
    "ft53": (53, 6905),
    "ft70": (70, 38673),
    "ftv33": (34, 1286),
    "ftv35": (36, 1473),
    "ftv38": (39, 1530),
    "ftv44": (45, 1613),
    "ftv47": (48, 1776),
    "ftv55": (56, 1608),
    "ftv64": (65, 1839),
    "ftv70": (71, 1950),  # UWAGA: Zmienione na 1950 zgodnie z tabelą
    "ftv90": (91, 1579),
    "ftv100": (101, 1788),
    "ftv110": (111, 1958),
    "ftv120": (121, 2166),
    "ftv130": (131, 2307),
    "ftv140": (141, 2420),
    "ftv150": (151, 2611),
    "ftv160": (161, 2683),
    "ftv170": (171, 2755),
    "kro124": (124, 36230),
    "p43": (43, 5620),
    "rbg323": (323, 1326),
    "rbg358": (358, 1163),
    "rbg403": (403, 2465),
    "rbg443": (443, 2720),
    "ry48p": (48, 14422)
}


def generate_tsplib_solutions():
    print(f"{'Instancja':<12} | {'Miasta':<6} | {'Opt. Koszt':<10} | Status")
    print("-" * 45)

    for name, (dim, cost) in atsp_solutions.items():
        filename = f"{name}.opt.tour"

        try:
            with open(filename, "w") as f:
                # Nagłówek TSPLIB
                f.write(f"NAME : {name}.opt.tour\n")
                f.write("TYPE : TOUR\n")
                f.write(f"DIMENSION : {dim}\n")
                f.write(f"COMMENT : Optimal tour cost is {cost}\n")
                f.write("TOUR_SECTION\n")

                # Zapisujemy sztuczną trasę (1 do N) na potrzeby zachowania formatu pliku.
                # Do sprawdzenia poprawności algorytmu i tak odczytuje się 'COMMENT' wyżej.
                for i in range(1, dim + 1):
                    f.write(f"{i}\n")

                f.write("-1\n")
                f.write("EOF\n")

            print(f"{name:<12} | {dim:<6} | {cost:<10} | Utworzono")
        except Exception as e:
            print(f"{name:<12} | BŁĄD: {e}")


if __name__ == "__main__":
    generate_tsplib_solutions()
    print("\nZakończono! Wszystkie pliki .opt.tour z tabeli zostały wygenerowane.")