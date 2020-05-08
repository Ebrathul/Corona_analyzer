import numpy as np
import pycountry
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import scipy.signal as signal

# generate data file containing ["Date", "Country", "ISO", "Confirmed", "Recovered", "Deaths"]
def get_data(save= True):
  dataurl = "https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv"

  df1 = pd.read_csv(dataurl, usecols = ["Date", "Country", "Confirmed", "Recovered", "Deaths"])
  print(df1)

  list_countries = df1['Country'].unique().tolist()
  print("Count of countries: ", len(list_countries), list_countries)

  country_code = {}  # Dict for country names and their ISO
  print(len(df1[df1['Country']== "Germany"]), df1[df1['Country']== "Germany"])

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
  # print(df1)

  # sort colums
  df1 = df1[["Date", "Country", "ISO", "Confirmed", "Recovered", "Deaths"]]
  if save == True:    
    df1.to_csv("ISO_Data.csv", index_label = "index")
  return df1


# get numerical valus from data and set confirmed to daily
def get_country_data(iso, data, daily = False):
  data = data[data['ISO'] == iso].to_numpy()

  if daily == True: # create increase numbers per day
    dataset = np.copy(data[: , 3:]) # get data from Dataset // use np.copy() if fails  
    for i in range(len(dataset)):
      if i > 0:
        dataset[i, 0] =  data[i , 3] - data[i - 1 , 3]  # cal. number of cases per day  
      else:
        dataset[i] = data[0 , 3]    # first datapoint set to zero
    return dataset
    
  elif daily == False:
    dataset = data[:, 3:] # return total confirmes cases
    return dataset
  else:
    pass



# get data for mutliple countries in one array
def get_multi_country_data(data, iso):
  # print(len(data), len(data)/185, data.shape[1], len(iso))
  country_data = np.zeros((int(len(data)/185), data.shape[1]-3, len(iso))) # only numeric data colums
  for i in range(len(iso)):
    country_data[1:, :, i] = get_country_data(iso[i], data, daily=True)  # [index, colum, country]
  # print(len(country_data[:, :, :]), country_data[:, :, :], country_data.shape)
  return country_data


# FFT
def get_fft_data(country_data):
  freq_country_data = np.zeros((country_data.shape[0], country_data.shape[1], country_data.shape[2]))
  fft_country_data = np.zeros((country_data.shape[0], country_data.shape[1], country_data.shape[2]))
  fft_country_data_rel = np.zeros((country_data.shape[0], country_data.shape[1], country_data.shape[2]))
  fft_freq = 1 / np.abs(np.fft.fftfreq(country_data[:, 0, 0].shape[-1]))
  
  for i in range(country_data.shape[1]):
    for j in range(country_data.shape[2]):
      fft_country_data[:, i, j] = np.abs(np.fft.fft(country_data[:, i, j], norm="ortho"))
      freq_country_data[:, i, j] = fft_freq
      ###########################################
      # DETREND
      # signal.detrend(fft_country_data[:, i, j], axis=-1, type='linear', overwrite_data = True)  # remove slope from fft 
      # fft_country_data[1:, i, j] = np.diff(fft_country_data[:, i, j], axis=0)
      meanFFT = np.mean(fft_country_data[:, i, j], axis=0)
      fft_country_data_rel[:, i, j] = fft_country_data[:, i, j] / meanFFT
  return freq_country_data, fft_country_data, fft_country_data_rel


#################################################
# main programm
#################################################
# variables
iso = ["DEU", "ITA", "GBR", "USA", "CHN", "RUS"]  # defines which countries will be evaluated


# df1 = get_data(save=True) 
df1 = pd.read_csv("ISO_Data.csv", index_col = "index") 
# print(df1, len(df1), df1.shape)
country_data = get_multi_country_data(df1, iso)  # [index, colum, country]
freq_country_data, fft_country_data, fft_country_data_rel = get_fft_data(country_data)


# Plot New Cases
fig = plt.figure()
ax = fig.add_subplot(111)
# ax.set_xlim(0, 15)
# ax.set_ylim(0, 3e5)
ax.set_xlabel("Day")
ax.set_ylabel("Daily new cases")
# ax.ticklabel_format(axis= "Y", style = "sci", scilimits = (0,0))
ax.set_title("New confirmed cases")
ax.plot(np.arange(len(country_data[:, 2, 0])), country_data[:, 0, :])
ax.legend(iso)
fig.savefig('New_Cases.png')


# Plot Dead
fig = plt.figure()
ax = fig.add_subplot(111)
# ax.set_xlim(0, 15)
# ax.set_ylim(0, 3e5)
ax.set_xlabel("Day")
ax.set_ylabel("Count of dead")
# ax.ticklabel_format(axis= "Y", style = "sci", scilimits = (0,0))
ax.set_title("Dead")
ax.plot(np.arange(len(country_data[:, 2, 0])), country_data[:, 2, :])
ax.legend(iso)
fig.savefig('Dead.png')


# Plot FFT 
fig = plt.figure()
ax = fig.add_subplot(111)
# ax.set_xlim(0, 15)
# ax.set_ylim(0, 3e5)
ax.set_xlabel("Day")
ax.set_ylabel("Frequ. count")
# ax.ticklabel_format(axis= "Y", style = "sci", scilimits = (0,0))
ax.set_title("Frequency of confirmed cases")
ax.plot(freq_country_data[:, 0, :], fft_country_data[:, 0, :])
ax.legend(iso)
fig.savefig('FFT.png')


# Plot FFT Relative
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlim(0, 15)
ax.set_ylim(0, 2)
ax.set_xlabel("Day")
ax.set_ylabel("Rel frequ. count")
# ax.ticklabel_format(axis= "Y", style = "sci", scilimits = (0,0))
ax.set_title("Rel frequency of confirmed cases")
ax.plot(freq_country_data[:, 0, :], fft_country_data_rel[:, 0, :])
ax.legend(iso)
fig.savefig('FFT_rel.png')
