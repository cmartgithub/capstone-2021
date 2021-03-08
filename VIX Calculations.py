#!/usr/bin/env python
# coding: utf-8

# # Python Script to Calculate VIX

# ### Import Data

# In[3]:


import processData
import datetime
import pandas as pd
import numpy as np
import math
import sys

def toCSV(array, filename):
	np.savetxt(filename+".csv",[array],delimiter=",",fmt='%.18e')


for m in range(0, 9):
	VIX_array = []
	count = 0
	for l in range(0, 15):

		ticker_num = m
		date_num = l
		#ticker_num = int(ticker_num)
		#date_num = int(date_num)

		tickers = processData.grabTickers('tickersymbs.txt')
		#print(tickers)
		#Return the access dates and nearterm, and nextterm call expry dates
		accessdate, nearterm, nextterm = processData.parse_file('Dates.txt')

		#TESTING
		near, next = processData.grabDataPaths(tickers[ticker_num],accessdate[date_num],nearterm[date_num],nextterm[date_num])
		near_term_call_strike,next_term_call_strike, near_term_put_strike, next_term_put_strike,near_term_call_mid,next_term_call_mid,near_term_put_mid,next_term_put_mid = processData.grabData(near,next)


		# ### Time to Expiration

		# In[2]:


		M_current_day = 854;
		M_settlement_day = 900;
		date_current = datetime.datetime.strptime(accessdate[date_num],'%Y-%m-%d')
		date_near = datetime.datetime.strptime(nearterm[date_num],'%Y-%m-%d')
		date_next = datetime.datetime.strptime(nextterm[date_num],'%Y-%m-%d')

		M_other_days_near_days = (date_near - date_current)*1440;
		M_other_days_near = M_other_days_near_days.days;
		M_other_days_next_days = (date_next - date_current)*1440;
		M_other_days_next = M_other_days_next_days.days;

		T1 = (M_current_day + M_settlement_day + M_other_days_near)/525600;
		T1 = float(T1)
		T2 = (M_current_day + M_settlement_day + M_other_days_next)/525600;
		T2 = float(T2)


		# ### Risk-Free Interest Rates

		# In[3]:


		file = open('interest_rate.txt', "r")
		date = []
		rates = []
		for line in file:
		    access, interest = line.split(',')
		    date.append(access)
		    rates.append(interest)

		length = len(date)
		for i in range(0, length-1):
		    if(date[i] == accessdate[0]):
		        interest_rate = rates[i]

		interest_rate = float(interest_rate)


		# ### Forward Index Level

		# In[4]:


		# near term
		length = len(near_term_call_mid)
		for i in range(1, length):
		    diff0 = near_term_call_mid[i-1] - near_term_put_mid[i-1]
		    diff0 = abs(diff0)
		    diff1 = near_term_call_mid[i] - near_term_put_mid[i]
		    diff1 = abs(diff1)
		    if(diff1 < diff0):
		        strike_price_near = float(near_term_call_strike[i])
		        call_price_near = float(near_term_call_mid[i])
		        put_price_near = float(near_term_put_mid[i])
		        
		# next term
		length = len(next_term_call_mid)
		for i in range(1, length):
		    diff0 = next_term_call_mid[i-1] - next_term_put_mid[i-1]
		    diff0 = abs(diff0)
		    diff1 = next_term_call_mid[i] - next_term_put_mid[i]
		    diff1 = abs(diff1)
		    if(diff1 < diff0):
		        strike_price_next = float(next_term_call_strike[i])
		        call_price_next = float(next_term_call_mid[i])
		        put_price_next = float(next_term_put_mid[i])

		F1 = strike_price_near + (math.exp(interest_rate*T1)*(call_price_near - put_price_near))
		F2 = strike_price_next + (math.exp(interest_rate*T2)*(call_price_next - put_price_next))

		# Strike Price Immediately below Foward Index Level F1
		if((F1 - math.floor(F1)) >= 0.5):
		    K_01 = float(math.floor(F1) + 0.5)
		else:
		    K_01 = float(math.floor(F1))
		    
		# Strike Price Immediately below Foward Index Level F2
		if((F2 - math.floor(F2)) >= 0.5):
		    K_02 = float(math.floor(F2) + 0.5)
		else:
		    K_02 = float(math.floor(F2))

		K_01 = "{:.2f}".format(K_01)
		K_02 = "{:.1f}".format(K_02)


		# ### Update Data

		# In[5]:


		# Updated Near Term Data
		new_near_term_put_strike = []
		new_near_term_put_mid = []
		new_near_term_call_strike = []
		new_near_term_call_mid = []

		length = len(near_term_put_strike)
		saw_put = 0
		saw_call = 0

		for i in range(0,length):
		    if(near_term_put_strike[i] != K_01 and saw_put == 0):
		        new_near_term_put_strike.append(near_term_put_strike[i])
		        new_near_term_put_mid.append(near_term_put_mid[i])
		    else:
		        saw_put = 1
		    
		    if(saw_call == 1):
		        new_near_term_call_strike.append(near_term_call_strike[i])
		        new_near_term_call_mid.append(near_term_call_mid[i])
		        
		    if(near_term_call_strike[i] == K_01):
		        new_near_term_call_strike.append(near_term_call_strike[i])
		        new_near_term_call_mid.append(near_term_call_mid[i])
		        saw_call = 1
		        
		near_term_mid = np.concatenate((new_near_term_put_mid, new_near_term_call_mid))
		near_term_strike = np.concatenate((new_near_term_put_strike, new_near_term_call_strike))

		# Update Next Term Data
		new_next_term_put_strike = []
		new_next_term_put_mid = []
		new_next_term_call_strike = []
		new_next_term_call_mid = []

		length = len(next_term_put_strike)
		saw_put = 0
		saw_call = 0

		for i in range(0,length):
		    if(next_term_put_strike[i] != float(K_02) and saw_put == 0):
		        new_next_term_put_strike.append(next_term_put_strike[i])
		        new_next_term_put_mid.append(next_term_put_mid[i])
		    else:
		        saw_put = 1
		    
		    if(saw_call == 1):
		        new_next_term_call_strike.append(next_term_call_strike[i])
		        new_next_term_call_mid.append(next_term_call_mid[i])
		        
		    if(next_term_call_strike[i] == float(K_02)):
		        new_next_term_call_strike.append(next_term_call_strike[i])
		        new_next_term_call_mid.append(next_term_call_mid[i])
		        saw_call = 1
		        
		next_term_mid = np.concatenate((new_next_term_put_mid, new_next_term_call_mid))
		next_term_strike = np.concatenate((new_next_term_put_strike, new_next_term_call_strike))


		# ### Calculate VIX

		# In[6]:


		# Change Values to Floats
		near_term_strike = near_term_strike.astype(float)
		near_term_mid = near_term_mid.astype(float)
		next_term_strike = next_term_strike.astype(float)
		next_term_mid = next_term_mid.astype(float)

		# Near Term omega^2
		length = len(near_term_strike)
		near_sum = 0
		for i in range(0,length):
		    if(i == 0):
		        near_sum = near_sum + (((near_term_strike[i+1] - near_term_strike[i])/(near_term_strike[i]**2))*math.exp(interest_rate*T1)*near_term_mid[i])
		    elif(i == length-1):
		        near_sum = near_sum + (((near_term_strike[i] - near_term_strike[i-1])/(near_term_strike[i]**2))*math.exp(interest_rate*T1)*near_term_mid[i])
		    else:
		        near_sum = near_sum + ((((near_term_strike[i+1] - near_term_strike[i-1])/2)/(near_term_strike[i]**2))*math.exp(interest_rate*T1)*near_term_mid[i])

		K_01 = float(K_01)
		omega_2_near = (2/T1)*(near_sum) - ((1/T1)*((F1/K_01)-1)**2)        

		# Next Term omega^2
		length = len(next_term_strike)
		next_sum = 0
		for i in range(0,length):
		    if(i == 0):
		        next_sum = next_sum + (((next_term_strike[i+1] - next_term_strike[i])/(next_term_strike[i]**2))*math.exp(interest_rate*T2)*next_term_mid[i])
		    elif(i == length-1):
		        next_sum = next_sum + (((next_term_strike[i] - next_term_strike[i-1])/(next_term_strike[i]**2))*math.exp(interest_rate*T2)*next_term_mid[i])
		    else:
		        next_sum = next_sum + ((((next_term_strike[i+1] - next_term_strike[i-1])/2)/(next_term_strike[i]**2))*math.exp(interest_rate*T2)*next_term_mid[i])

		K_02 = float(K_02)
		omega_2_next = (2/T2)*(next_sum) - ((1/T2)*((F2/K_02)-1)**2)

		# Calculate VIX
		N_T1 = 35924
		N_T2 = 46394
		N_30 = 43200
		N_365 = 525600

		VIX = 100*math.sqrt(((T1*omega_2_near*((N_T2-N_30)/(N_T2-N_T1)))+(T2*omega_2_next*((N_30-N_T1)/(N_T2-N_T1))))*(N_365/N_30))
		VIX = "{:.2f}".format(VIX)
		VIX = float(VIX)
		print(VIX,type(VIX))
		VIX_array.append(VIX)
		
		count = count + 1
		if(count == len(accessdate)-1):
			#VIX_array = np.array(map(float, VIX_array))
			toCSV(VIX_array, str(tickers[m]))

		# In[ ]:




