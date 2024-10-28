# %%
import pandas as pd
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import locale
locale.setlocale(locale.LC_ALL, '') 
import plotly.graph_objects as go


accountname = '2024_Umsatzliste' # set filename of the csv

# 0 or less means analyse all months
number_of_last_months_to_analyse = 12

def quick_category_analyse(cat,desc=""):
    excursions = data[data[category] == cat].sort_values(amount,ascending=True)

    excursions.plot.barh(
        figsize=(12,12),
        x=desc,
        y=amount,
        legend=None,
    )
    plt.show()

    return excursions

csv_file= accountname+".csv"
headerSize = 4
data = pd.read_csv(csv_file, index_col='Buchungsdatum',
# data = pd.read_csv(csv_file,
                   header=headerSize, sep=',', quoting=1, parse_dates=True, dayfirst=True)
print(data.head())


# # Read metadata
with open(csv_file,"r") as f:
    reader = csv.reader(f)
    metadata = {}
    for i, row in enumerate(reader):
        if i<3:
            if "Kontostand" in row[0]:
                end_balance = float(row[1][:-2].replace(".","").replace(",","."))

end_date = datetime.strptime(data.iloc[0][0],"%d.%m.%y").date()
start_date = datetime.strptime(data.iloc[-1][0],"%d.%m.%y").date()


print("start:",start_date)
print("end:",end_date)
print("end balance:",end_balance)


# ## Named Columns
# We define the columns of the csv file for better readability

destination = "Zahlungsempfänger*in"
source = "Zahlungspflichtige*r"
amount = "Betrag (€)"
cause = "Verwendungszweck"
balance = "Kontostand (EUR)"
category = "Kategorie"

# ### Cleanup


# Fix US / EU decimal-point/comma
# print(data[amount])
data[amount] = data[amount].str.replace('.','')
data[amount] = data[amount].str.replace(',','.')
data[amount] = data[amount].astype('float')

# avoid nan being interpreted as float in specific columns
data[destination] = data[destination].astype(str)
data[cause] = data[cause].astype(str)

# data.head()

# ### Remove small transactions to avoid noise

data = data[abs(data[amount]) > 0.01]

# ### Inverse Dataframe to have first day first and filter by time-range

from dateutil.relativedelta import relativedelta
if number_of_last_months_to_analyse > 0:
    start_date = end_date - relativedelta(months=number_of_last_months_to_analyse)
    
print(f"Analysing time range: {start_date} -> {end_date}")
data = data.loc[str(start_date):str(end_date)]
data = data.iloc[::-1]


fr = data.index[0]
to = data.index[-1]
# print(fr,"->",to)

# ### Compute balance at each transaction

data_balance = data[amount].sum().round(2)
start_balance = end_balance - data_balance
data[balance] = data[amount].cumsum()+start_balance


# print("start",start_balance)
# print("end",end_balance)
# print("balance during csv timespan",data_balance)

# ## Balance over time

# %%
# data[balance].plot(
#     title='Account balance',
#     grid=True,
#     figsize=(20,8)
# )
# ## Breakdown by transaction destination

# print(data.groupby(destination).agg({amount:"sum"}))
# print(data)
outgroup = data[data[amount]<0].groupby(destination).agg({amount:"sum"})

# Short the names
outgroup.index = [str(i)[:50] for i in outgroup.index]
# outgroup = outgroup.sort_values(amount,ascending=False)
gutschrift = outgroup[amount] > 0
colors = list( map(lambda x: "g" if x else "r" , gutschrift))

# outgroup[outgroup[amount].abs() > 50].plot.barh(
#     figsize=(10,60),
#     title=u'Aggregierte Zahlungen ab 50€ (%i.%i.%i - %i.%i.%i)' % (fr.day, fr.month, fr.year, to.day, to.month, to.year)
#   )

ingroup = data.groupby(source).agg({amount:"sum"})

# ingroup[ingroup[amount]>0].plot.barh(
#     figsize=(10,60),
#     title=u'Einkünfte (%i.%i.%i - %i.%i.%i)' % (fr.day, fr.month, fr.year, to.day, to.month, to.year)
# )

in_categories = {
    "Gehalt": [
        "Christoph Gerhardt",
        "Milica Gerhardt",
    ],
    "Miete": [
        "Alexander",
        "Helga",
    ],
    }
# %%
def mapInCategory(x):
    # use transaction details to map to a category
    p = x[source].lower()
    c = x[cause].lower()
    
    # mappings by category
    for cat, cat_words in in_categories.items():
        if any(map(lambda r: r.lower() in p, cat_words)) or any(map(lambda r: r.lower() in c, cat_words)):
            return cat
    # return in_categories["Sonstiges"][0]
    return p

data[category] = data.apply(lambda x: mapInCategory(x), axis=1)
# Sum the entries for each category in the 'amount' column
inbyCategory = data[data[amount] > 0]
inbyCategory = inbyCategory.groupby(category)
inbyCategoryTotal = inbyCategory.agg({amount:"sum"})
# Prepare data for Sankey diagram
labels = [str(i)[:50] for i in inbyCategoryTotal.index] + ["Total Income"]
sources = list(range(len(inbyCategoryTotal)))
targets = [len(inbyCategory)] * len(inbyCategoryTotal)
values = inbyCategoryTotal[amount].abs().tolist()

# Create Sankey diagram
fig = go.Figure(data=[go.Sankey(
    valueformat = ".0f",
    valuesuffix = "€",    
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
    ))])

fig.update_layout(title_text="Eingänge nach Kategorie", font_size=10)
fig.show()



# Prepare data for Sankey diagram
labels = list(ingroup.index) + ["Total Income"]
sources = list(range(len(ingroup)))
targets = [len(ingroup)] * len(ingroup)
values = ingroup[amount].tolist()

# Create Sankey diagram
fig = go.Figure(data=[go.Sankey(
    valueformat = ".0f",
    valuesuffix = "€",    
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
    ))])

fig.update_layout(title_text="Eingänge nach ", font_size=10)
fig.show()

# ## Breakdown by Category
# We use some heuristics on the tranasaction details to put them into different categories.


#%% 
out_categories = {
    "Gastronomie": [
        "restaurant",
        "gastro",
        "dean david",
        "cafe",
        "baeckerei",
        "coffee fellows",
        "jim block",
        "don qui",
        "Osteria",
        "subway",
        "backhaus",
        "burger king",
        "campus suite",
        "juice.more",
        "Back",
        "Avni Terhani",
        "vegan",
        "thai",
        "indisch",
        "schortemuehle",
        "metzgerei",
        "kantine",
        "kaffee",
        "backshop",
        "bistro",
        "imbiss",
        "pizza",
        "baecker", 
        "bäcker",    
        "ibras",
        "ditsch",
        "kfc",
        "mcdonald",
        "starbucks",
        "vapiano",
        "nordsee",
        "block house",
        "food",
        "catering"
        "coffee",
        "beer",
        "eismanufaktur",
        "bar",
        "schoko",
        
    ],
    "Dienstreisen": [
        "bonn",
        "seattle",
        "dienstreise",
        "shake shack",
        "scoom",
        "orca",
        "7-eleven",
        "walgreens",
    ],
    "Supermarkt": [
        "lidl",
        "aldi",
        "edeka",
        "alnatura",
        "rewe",
        "norma",
        "netto",
        "kaufland",
        "penny",
        "tegut",
        "maerkte",
    ],
    "Drogerie": [
        "mueller",
        "müller",
        "rossmann",
        "dm",
        "action",
        "douglas",
        "parfuemerie",
        "maec geiz",
        "mäc geiz",
        "mc pfennig",
    ],
    "Baumarkt": [
        "bauhaus",
        "obi",
        "hornbach",
        "hellweg",
        "toom",
        "globus",
        "mano",
        "pro shop",
        "glas strack",
    ],
    "Online Shopping":[
        "otto",
        "conrad elec",
        "amzn mktp",
        "amazon",
        "zalando",
        "ebay",
        "aliexpress",
        "asics",
    ],
    "Transport": [
        "FERNVERKEHR",
        "flixbus",
        "bahn",
        "PAYPAL .DBVERTR",
    ],
    "Reise": [
        "booking",
        "hotel",
        "airbnb",
        "mallorca",
        "iberostar",
        "ryanair",
        "airport",
        "easyjet",
        "lufthansa",
        "airberlin",
        "tuifly",
        "eurowings",
        "cala",
        "spain",
        "allgaeu",
        "wizz",
        "fly",
        "fraport",
        "petro",
        "palma",
        "madrid",
        "balear",
        "santanyi",
        "portal interactiv",
        "eDreams",
        
    ],
    "Serbien": [
        "serbia",
        "komerc",
        "maxi",
        "gornji",
        "rs",
        "serbien",
        "belgrad",
        "beograd",
        "nbg",
        "novi",
        "kragujevac",
        "kraljevo",
        "krusevac",
        "nis",
        "cacak",
        "banj",
        "lilly",
        "jeva"
    ],  
    "Ausflug":[
        "zoo",
        "tierpark",
        "schwimmbad",
        "therme"
        "ega",
        "freizeitpark",
        "kino",
        "lichtspiele",
        "theater",
        "schwimmhalle",
        "harz",
        "hochseilgarten",
        "kletterpark",
        "wernigerode",
        "freibad",
        "geiselwind",
        "brocken",
        ],
    
    "Project": [
        "openai",
        "google.cloud",
        "github",
    ],
    
    "Hobby": [
        "germania",
        "tanz",
    ],
    "Unterhaltung": [
        "magellan",
        "Amazon Prime",
        "paypal .steam",
        "netflix",
        "spotify",
        "sky",
        "disney",
        "adyen",
    ],
    "Gesundheit": [
        "apotheke",
        "krankenversicherung",
        "krank",
        "arzt",
    ],
    "Bargeld": [
        "bargeld",
        "automat",
        "cash"
    ],
    "DKB": [
        "DKB",
        "KREDITBANK",
    ],
    "Kleidung":[
        "tk maxx",
        "deichmann",
        "primark",
        "h.m",
        "h.amp.m",        
        "c&a",
        "kik",
        "decathlon",
        "takko",
        "ernsting",
    ],
    "Möbel":[
        "ikea",
        "moebel",
        "moebelhaus",
        "roller",
        "xxxl",
        "poco",
        "porta",
        "sconto",
        "k+b",
    ],
    "Haus und Garten":[
        "vs",
        "mollie",
        "mc garden",
    ],
    "Nebenkosten": [
        "Kredit", 
        "Gebäude",
        "Abfall",
        "wavi",
        "hubert kupfer"
        ],
    "Energie":[
        "leu", 
        "eprimo",
        "yippie",
        "vattenfall",
    ],
    "Versicherung":[
        "astra",
        "adam riese",
        "neodigital"
    ],
    "Auto":[
        "aral",
        "total",
        "agip",
        "tank",
        "omv",
        "kfz",
    ],
    "Mobilfunk":["handyaufladung"
    ],
    "Kita": [
        "kita",
        "stadt ilmenau",
        "stadtverwaltung ilmenau",
    ],
    "Mittagessen": ["mensa", "henry schuetze"], 
    "investment": [],
    "emergency_fund":[],
    "Paypal": ["paypal"],
    "card_payment": [],
    "Sonstiges": [ # populated automatically
    ]
}

def mapOutCategory(x):
    # use transaction details to map to a category
    p = x[destination].lower()
    c = x[cause].lower()
    
    # mappings by category
    for cat, cat_words in out_categories.items():
        if any(map(lambda r: r.lower() in p, cat_words)) or any(map(lambda r: r.lower() in c, cat_words)):
            return cat
    return p

data[category] = data.apply(lambda x: mapOutCategory(x), axis=1)

print(len(data[category].unique()),"out_categories")

print("============ uncategorized =================")
s = 0
# for x in data[category].unique():
#     ok = False
    
#     for cat in out_categories.keys():
#         if x == cat:
#             ok = True

#     if not ok:
#         print(x)
#         idx = data[category] == x
#         s = s + abs(data[idx][amount].sum())
        


# Breakdown by category
# Ignore groups below minimum amount
minimum_amount = 200
byCategory = data.groupby(category).agg({amount:"sum"})
byCategory = byCategory[abs(byCategory[amount]) > minimum_amount]

# outgoing transactions (amount is negative)
costs = byCategory[byCategory[amount] < 0]
# invert the amounts for better readability
costs.loc[:, amount] = -costs[amount]

total_costs = costs[amount].sum()
costs.plot.pie(
    figsize=(12,12),
    y=amount,
    legend=None,
    ylabel="",
    # autopct='%1.1f%%',
    title=u'Ausgaben nach Kategorie (%i.%i.%i - %i.%i.%i)' % (fr.day, fr.month, fr.year, to.day, to.month, to.year),
    startangle=15,  # Rotate the start of the pie chart
    wedgeprops={'edgecolor': 'white', 'width':0.4},  # Add edge color for better readability
    textprops={'fontsize': 11},  # Increase font size for better readability
    labels=[f"{label} | {int(value):n} € | {round(value/total_costs*100,1)} %" for label, value in zip(costs.index, costs[amount])],
    # pctdistance=1.1,  # Position the percentage labels closer to the center
    labeldistance=1.05,  # Position the category labels further from the center
)
# Draw a circle at the center to make it a donut chart
# centre_circle = plt.Circle((0,0),0.70,fc='white')
fig = plt.gcf()
# fig.gca().add_artist(centre_circle)

plt.show()

# byCategory[byCategory[amount] > 0].plot.pie(
#     figsize=(12,12),
#     y=amount,
#     legend=None,
#     title=u'Nach Kategorie Aggregiertes Einkommen (%i.%i.%i - %i.%i.%i)' % (fr.day, fr.month, fr.year, to.day, to.month, to.year)
# )
# plt.show()


# byCategory.plot.barh(
#     figsize=(6,40),
#     grid=True,
#     title=u'Nach Kategorie Aggregierte Zahlungen (%i.%i.%i - %i.%i.%i)' % (fr.day, fr.month, fr.year, to.day, to.month, to.year)
# )
# plt.show()


# quick_category_analyse("Paypal",desc=cause)

# quick_category_analyse("Reise", desc=cause)

# quick_category_analyse("Energie", desc=destination)


# %%
