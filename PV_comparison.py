import math
import matplotlib.pyplot as plt

# =============================================
# 1) Gemeinsam genutzte Einstellungen/Variablen
# =============================================
r = 0.0412             # Kalkulationszins
n = 30                 # 30 Jahre
growth = 0.03          # 3% Strompreissteigerung

# Kaufpreise
cost_offer1 = 23364
cost_offer2 = 32325
cost_offer3 = 25850

# Referenz-Verbrauch
# (wir variieren das später, z.B. 9.3, 10.5, 12.0)
def base_stromkosten_y1(kWh_per_year):
    """
    Berechnet die Stromkosten (ohne PV) im Jahr 1,
    für den angegebenen Jahresverbrauch kWh_per_year
    entsprechend der WP+HS-Tarife ~19,44 + 29,19 ct/kWh gemittelt.
    Der Einfachheit halber nutzen wir denselben gemittelten Approach wie bisher.
    """
    # Bisher ~2.247 € bei 9.300 kWh => ~0.2415 €/kWh im Durchschnitt
    # Also lineare Skalierung:
    avg_price_per_kWh = 2247 / 9300  # ~0.2415 €/kWh
    return kWh_per_year * avg_price_per_kWh

def cost_without_pv(i, basecost):
    """
    Stromkosten ohne PV im Jahr i,
    basierend auf "basecost" (Kosten im Jahr 1) und 3% Wachstum.
    """
    return basecost * ((1 + growth)**(i - 1))

def cost_with_pv_1_3(i, basecost):
    """
    Angebot 1 & 3: 30% Netzbezug zum normalen (wachsenden) Tarif.
    => 30% von cost_without_pv(i, basecost).
    """
    return 0.30 * cost_without_pv(i, basecost)

def cost_with_pv_2_full30(i):
    """
    Angebot 2 (30 Jahre Fix): 30% Netzbezug = 2,79 MWh * 0.12 €/kWh ~ 334.8 €/Jahr
    => fix, kein Wachstum.
    """
    return 334.8

def cost_with_pv_2_custom(i, basecost, guarantee_years):
    """
    Angebot 2 in einer Variante, wo die 12 ct/kWh
    NUR bis 'guarantee_years' gilt. Danach normaler Tarif mit 3% Wachstum.
    """
    if i <= guarantee_years:
        # Fixpreis
        return 334.8
    else:
        # Ab guarantee_years+1 => normaler (wachs. Tarif) für 30% des Bedarfs
        return 0.30 * cost_without_pv(i, basecost)

def npv_berechnen(kaufpreis, cost_func, basecost):
    """
    Summiert diskontiert (Stromkosten-ohne - Stromkosten-mit) - Kaufpreis
    über 30 Jahre.
    """
    npv = -kaufpreis
    for i in range(1, n+1):
        cost_ohne = cost_without_pv(i, basecost)
        cost_mit  = cost_func(i)
        ersparnis = cost_ohne - cost_mit
        npv += ersparnis / ((1 + r)**i)
    return npv

# =============================================
# 2) Szenario A: Variation des Jahresverbrauchs
# =============================================

verbraeuche = [9.3, 10.5, 12.0]  # in MWh

npv_values_A = {
    # Key: (Verbrauch, "Angebot1" o.ä.) => Value: NPV
}

# Wir nehmen an, dass Angebot2 hier *voll 30 Jahre* Preisgarantie hat.
for v in verbaeuche:
    # berechne basecost für Jahr1
    basecost = base_stromkosten_y1(v*1000)  # MWh -> kWh
    # NPV für Angebot1
    f1 = lambda i: cost_with_pv_1_3(i, basecost)
    npv1 = npv_berechnen(cost_offer1, f1, basecost)

    # NPV für Angebot2 (30J fix)
    f2 = lambda i: cost_with_pv_2_full30(i)
    npv2 = npv_berechnen(cost_offer2, f2, basecost)

    # NPV für Angebot3
    f3 = lambda i: cost_with_pv_1_3(i, basecost)
    npv3 = npv_berechnen(cost_offer3, f3, basecost)

    npv_values_A[(v, "A1")] = npv1
    npv_values_A[(v, "A2")] = npv2
    npv_values_A[(v, "A3")] = npv3

# => Erstellen eines Balkendiagramms, gruppiert nach Verbrauch
plt.figure()

x_positions = []
labels = []
heights = []

group_width = 0.6
offsets = [-0.2, 0.0, 0.2]  # 3 Angebote pro Gruppe

idx = 0
for v in verbaeuche:
    # pro Gruppe (Verbrauch) drei Balken: A1, A2, A3
    for j, offer_name in enumerate(["A1", "A2", "A3"]):
        x = idx + offsets[j]
        x_positions.append(x)
        labels.append(f"{v}MWh-{offer_name}")
        val = npv_values_A[(v, offer_name)]
        heights.append(val)
    idx += 1

plt.bar(x_positions, heights, width=0.2)

# X-Achsen-Label etwas eleganter
plt.xticks([i for i in range(len(verbraeuche))],
           [f"{v} MWh/Jahr" for v in verbaeuche])

plt.title("Szenario A: NPV (30 J.) bei variablem Jahresverbrauch\n(Angebot2 behält 30J-Fixpreis)")
plt.ylabel("Barwert (Euro)")
plt.grid(True, axis='y')

# Einfacher Legenden-Hack: wir geben eine Legende aus
plt.legend(["Angebot1", "Angebot2", "Angebot3"], loc="best")

plt.show()


# =============================================
# 3) Szenario B: Kürzere Preisgarantie bei A2
# =============================================

guarantee_years_list = [10, 15, 20, 30]
# Wir fixieren den Stromverbrauch wieder auf 9.3 MWh
basecost_93 = base_stromkosten_y1(9300)

npv_values_B = {}

# Angebot1 + 3 ändern sich nicht (keine Variation),
# also berechnen wir sie einmal
fA1 = lambda i: cost_with_pv_1_3(i, basecost_93)
fA3 = lambda i: cost_with_pv_1_3(i, basecost_93)
npvA1 = npv_berechnen(cost_offer1, fA1, basecost_93)
npvA3 = npv_berechnen(cost_offer3, fA3, basecost_93)

for gy in guarantee_years_list:
    fA2_gy = lambda i: cost_with_pv_2_custom(i, basecost_93, gy)
    npvA2_gy = npv_berechnen(cost_offer2, fA2_gy, basecost_93)
    npv_values_B[gy] = npvA2_gy

# => Balkendiagramm: 1 Balken für A1, 1 Balken für A3, + 4 Balken für A2 in Varianten
plt.figure()

x_vals = [0, 1]  # Positionen für A1, A3
heights = [npvA1, npvA3]
labels = ["Angebot1", "Angebot3"]

# A2-Varianten
start_x = 2
for i, gy in enumerate(guarantee_years_list):
    x = start_x + i
    val = npv_values_B[gy]
    x_vals.append(x)
    heights.append(val)
    labels.append(f"A2_Guar{gy}")

plt.bar(x_vals, heights)
plt.xticks(x_vals, labels, rotation=30)

plt.title("Szenario B: NPV (30 J.) mit verkürzter Fixpreis-Garantie bei Angebot2 (9,3MWh/Jahr)")
plt.ylabel("Barwert (Euro)")
plt.grid(True, axis='y')
plt.show()
