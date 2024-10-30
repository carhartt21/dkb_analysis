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

    fig = go.Figure(data=[go.Pie(labels=excursions[destination], values=excursions[amount], hole=.3)])
    fig.update_layout(title_text=f"Breakdown of {cat} {desc}")
    fig.show()

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
data[amount] = data[amount].str.replace('.', '', regex=False)
data[amount] = data[amount].str.replace(',', '.', regex=False)
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
data = data.sort_index()
data = data.loc[str(start_date):str(end_date)]
data = data.iloc[::-1]


fr = data.index[0]
to = data.index[-1]
# print(fr,"->",to)

# ### Compute balance at each transaction

data_balance = data[amount].sum().round(2)
start_balance = end_balance - data_balance
balance = data[amount].cumsum()+start_balance

# ## Balance over time

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=data.index,
    y=balance,
    mode='lines',
    name='Account Balance'
))

fig.update_layout(
    title='Account Balance Over Time',
    xaxis_title='Date',
    yaxis_title='Balance (€)',
    template='plotly_white'
)

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
    "Paypal": ["paypal"],
    "Bargeldabhebung": [
        "bargeldabhebung", 
        "Sparkasse"
    ],
    "Sonstiges": [ # populated automatically
    ]
}

def mapOutCategory(x):
    # use transaction details to map to a category
    if x['Umsatztyp'] == "Eingang":
        return "Eingang"
    p = x[destination].lower()
    c = x[cause].lower()
    
    # mappings by category
    for cat, cat_words in out_categories.items():
        if any(map(lambda r: r.lower() in p, cat_words)) or any(map(lambda r: r.lower() in c, cat_words)):
            return cat
    return "Sonstiges"

data[category] = data.apply(lambda x: mapOutCategory(x), axis=1)

print("============ uncategorized =================")
uncategorized = data[data[category] == "Sonstiges"]
print(uncategorized[[destination, cause, amount]].sort_values(amount,ascending=True).head(10))
uncategorized.head(10)
print("==========================================")

# Breakdown by category
# Ignore groups below minimum amount
minimum_amount = 200
byCategory = data.groupby(category).agg({amount:"sum"})
byCategory = byCategory[abs(byCategory[amount]) > minimum_amount]

# %%
# outgoing transactions (amount is negative)
expenses = byCategory[byCategory[amount] < 0]
# invert the amounts for better readability
expenses.loc[:, amount] = expenses[amount].apply(lambda x: -x)

quick_category_analyse("Paypal",desc=cause)

# quick_category_analyse("Reise", desc=cause)

# quick_category_analyse("Energie", desc=destination)
#%%
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
    src = x.name.lower()
    # mappings by category
    for cat, cat_words in in_categories.items():
        if any(map(lambda r: r.lower() in src, cat_words)):
            return cat
    return "Sonstiges"
# %%

# data[category] = data.apply(lambda x: mapInCategory(x), axis=1)
ingroup = data[data[amount] > 0].groupby(source).agg({amount:"sum"})

ingroup[category] = ingroup.apply(lambda x: mapInCategory(x), axis=1)
total_income = ingroup[amount].sum()
# %%
labels = [str(i)[:30] for i in ingroup.index]
sources = []
targets = []
values = []

# %%
# First stage: from entries to categories
labels+=(list(ingroup[category].unique()))
for i, entry in enumerate(ingroup.index):
    cat = ingroup.loc[entry, category]
    cat_index = len(ingroup.index) + list(ingroup[category].unique()).index(cat)
    sources.append(i)
    targets.append(cat_index)
    values.append(ingroup.loc[entry, amount])

# %%

# Second stage: from categories to total income
labels.append("Gesamteinkommen")
total_income_index = len(ingroup.index) + len(ingroup[category].unique())
for cat in ingroup[category].unique():
    cat_index = len(ingroup.index) + list(ingroup[category].unique()).index(cat)
    sources.append(cat_index)
    targets.append(total_income_index)
    values.append(ingroup[ingroup[category] == cat][amount].sum())

    # Third stage: from total income to expense categories
print(len(labels),len(sources),len(targets),len(values))
    
# %%
# Third stage: from total income to total expenses
total_expenses_index = len(ingroup.index) + len(ingroup[category].unique()) + 1
labels.append("Gesamtausgaben")
cat_index = len(ingroup.index) + len(ingroup[category].unique()) + len(list(expenses.index)) + 1
sources.append(total_income_index)
targets.append(total_expenses_index)
values.append(total_income)


# %%
labels+=[str(i)[:30] for i in expenses.index]
for cat in expenses.index:
    cat_index = len(ingroup.index) + len(ingroup[category].unique()) + 2 + list(expenses.index).index(cat)
    sources.append(total_expenses_index)
    targets.append(cat_index)
    values.append(expenses.loc[cat, amount])

# %%
# Create Sankey diagram
fig = go.Figure(data=[go.Sankey(
    valueformat = ",.0f",  # Add thousand separator
    valuesuffix = "€",     
    # hovertemplate='{source}->{target}:{value}<extra></extra>',     
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
        # hovertemplate="{value}",
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        # hovertemplate="{source}->{target}:{value}",        
    )
)])
# fig.update_traces(hovertemplate=None)
fig.update_layout(title_text="Finanzübersicht", font_size=10)
fig.write_html("finances.html")

# fig.show()

