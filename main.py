import numpy as np
import pycountry
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt

def get_data(save= True):
    # get dataset
  dataurl = "https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv"

  df1 = pd.read_csv(dataurl, usecols = ["Date", "Country", "Confirmed", "Recovered", "Deaths"])
  print(df1)

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
  print(country_code)

  for k, v in country_code.items():
      df1.loc[(df1.Country == k), 'ISO'] = v
  print(df1)

  # sort colums
  df1 = df1[["Date", "Country", "ISO", "Confirmed", "Recovered", "Deaths"]]
  if save == True:    
    df1.to_csv("ISO_Data.csv", index_label = "index")
  return df1


def get_country_data(iso, data):
  data = (data[data['ISO'] == iso])
  return data.to_numpy()

# main program

#df1 = get_data(save=True)
df1 = pd.read_csv("ISO_Data.csv", index_col = "index")
print(df1)
iso = ["DEU"]
countryData = get_country_data(iso[0], df1)
print(len(countryData[:, 3]), countryData[:, 3])


#FFT

freq = 1/np.abs(np.fft.fftfreq(countryData[:, 3].shape[-1]))
FFTData = np.abs(np.fft.fft(countryData[:, 3])) 
meanFFT = np.mean(FFTData)
FFTData_rel = FFTData/meanFFT

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlim(0, 14)
ax.set_ylim(0, 2)
#ax.set_ylim(0, 5e5)
#ax.ticklabel_format(axis= "Y", style = "sci", scilimits = (0,0))
ax.set_title("Frequency of confirmed cases")
ax.plot(freq, FFTData_rel)
fig.savefig('FFT.png')


