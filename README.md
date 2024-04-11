# Code, data and Supplement for 'A Critical Survey of Research in Music Genre Recognition'

## Supplement PDF

Details on methods and current online locations for GTZAN

## Data 

* Bibliography `.bib` file
* `.csv` of survey data used in the paper

## Code 

Python code (>= 3.10) used for loading and querying the data 

* `mgrsurvey/*`: util code for loading 
* `queries.ipynb`: Jupyter notebook with queries 

To install dependencies in a virtual environment using the included `requirements.txt`
```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Primary requirements are pandas and the bibtexparser library, plus jupyterlab to run the notebook. 

Run 
```
jupyter lab
```
to launch jupyter and run the notebook in your browser. Alternatively if you have vscode set up to run notebooks, it should recommend the newly created venv by default. 