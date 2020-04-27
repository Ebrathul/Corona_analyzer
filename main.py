import numpy as np
import pycountry
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt

def get_data(save= False):
    # get dataset
  dataurl = "https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv"

  df1 = pd.read_csv(dataurl)
  # print(df1)

  list_countries = df1['Country'].unique().tolist()
  # print(len(list_countries), list_countries)

  country_code = {}  # Dict for country names and their ISO
  # print(df1[df1['Country']== "Germany"])

  # get iso code for each country
  for country in list_countries:
    try:
      country_data = pycountry.countries.search_fuzzy(country)
      # country_data is a list of objects of class pycountry.db.Country
      # The first item  ie at index 0 of list is best fit
      # object of class Country have an alpha_3 attribute
      code = country_data[0].alpha_3
      country_code.update({country: code})
      
    except:
      print('could not add ISO 3 code for ->', country)
      # If could not find country, make ISO code ' '
      country_code.update({country: ' '})
  # print(country_code)

  for k, v in country_code.items():
      df1.loc[(df1.Country == k), 'ISO'] = v
  # print(df1)
  
  if save == True:    
    df1.to_csv("/ISO_Data.csv")
  return df1

df1 = get_data(save=False)
