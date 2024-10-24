# DKB-Kontoauszug-Visualizer

Analyze .csv from your DKB bank account with Python Pandas.

![DKB Logo](https://upload.wikimedia.org/wikipedia/commons/d/d4/Deutsche_Kreditbank_AG_Logo_2016.svg)


---

## Features

* view your balance over the entire exported CSV time-range - or over the last N months
* view pie charts of your expenses and income
  * find out your largest expenses to optimise them
* categorise transactions with heuristics (e.g. miete, card_payment, investment, etc.)
  * what are the biggest positions within each category?
* privacy: everything is computed locally and offline on our computer. no servers or companies you need to trust
* security: it simply uses the CSV you exported. it cannot access your account in any way.

### 1. CSV Export

Select the largest time period on your main Girokonto (3 years) and export it all to CSV.

![csv Export](csv_export_DKB.png)

### 2. Save under `<my-name>.csv`

### 3. `jupyter lab DKB-Kontoauszug-Visualizer.ipynb`

### 4. Follow instructions in notebook and execute cells

---

## Contributing

The notebook may need updating, if the CSV format by DKB has changed.

In that case, please update the code and create a pull request to change it here for everyone.

This tool was shortly discussed on this [Reddit thread](https://www.reddit.com/r/Finanzen/comments/1041ycv/github_financeanalysisdkb_dkb_finanzen_lokal_und/). If anyone wants to extens the code and perhaps automate the extraction of the CSV from the bank, then this thread contains relevant information.
