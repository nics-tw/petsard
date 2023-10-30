# wrote by MA Ruiqiang and Hiroaki Kikuchi, 2021
#!/usr/bin/env python
# coding: utf-8
import pandas as pd
#import numpy as np
import sys

def quant(x):
	q = mets.quantile([0.25, 0.5, 0.75])
	if x <= q[0.25]: return 'Q1'
	elif x <= q[0.5]: return 'Q2'
	elif x <= q[0.75]: return 'Q3'
	else: return 'Q4'

if len(sys.argv) < 2:
	print (sys.argv[0], 'output.csv')
	sys.exit(0)

path = 'https://wwwn.cdc.gov/Nchs/Nhanes/2015-2016/'
xpt = ['DIQ_I.XPT', 'BMX_I.XPT', 'PAQ_I.XPT', 'GHB_I.XPT', 'DPQ_I.XPT', 'INQ_I.XPT']
df = pd.read_sas(path + 'DEMO_I.XPT')

for x in xpt:
	df = df.merge(pd.read_sas(path + x), on = 'SEQN')

# Delete row with unknown PY value (9999/99)
padlist = list(range(1, 6))
for i in padlist:
  df['PAD6'+str(15*i)][df['PAD6'+str(15*i)] == 9999] = 0
  df['PAQ6'+str(10+15*(i-1))][df['PAQ6'+str(10+15*(i-1))] == 99] = 0
  
mets =  (df['PAD615'] * df['PAQ610'] * 8 ).fillna(0)\
	+ (df['PAD630'] * df['PAQ625'] * 4).fillna(0) \
	+ (df['PAD645'] * df['PAQ640'] * 4).fillna(0) \
	+ (df['PAD660'] * df['PAQ655'] * 8).fillna(0) \
	+ (df['PAD675'] * df['PAQ670'] * 4).fillna(0)
df['METS'] = mets
df['QMETS'] = mets.map(quant)

# high Glycohemoglobin (%) or Ever told you have prediabetes (DIQ160), diabetes (DIQ010), insulin (DIQ050), or diabetic pills (DIQ070)
df['finflg'] = df.eval("LBXGH >= 6.5 or DIQ010 == 1 or DIQ050 == 1 or DIQ070 == 1").astype(int)

# older than 20 and no family had diabets (DIQ175A)
df2 = df.query('RIDAGEYR >= 20 and DIQ175A != 10')

# gen, age, race, education, marital, BMI, 鬱病, 貧困率, 血糖値, 活動量, 活動量四分位数, 糖尿病   
df3 = df2.loc[:,['RIAGENDR','RIDAGEYR','RIDRETH1','DMDEDUC2','DMDMARTL','BMXBMI','DPQ020','INDFMMPI','LBXGH', 'METS', 'QMETS', 'finflg']] 

df3['RIAGENDR'] = df2['RIAGENDR'].map({1: 'Male', 2: 'Female'})
df3['RIDRETH1'] = df2['RIDRETH1'].map({1: 'Mexican', 2: 'Hispanic', 3: 'White', 4: 'Black', 5: 'Other'})

df3['DMDEDUC2'] = df2['DMDEDUC2'].map({1: '9th', 2: '11th', 3: 'HighSchool', 4: 'College', 5: 'Graduate'})	# 9 'Missing' (3件) はNaN
df3['DMDMARTL'] = df2['DMDMARTL'].map({1:'Married', 2: 'Widowed', 3: 'Divorced', 4: 'Separated', 5: 'Never', 6: 'Parther'}) # 77 'refused' (1件)はNaN

df3['DPQ020'] = df2.eval('1 <= DPQ020 <= 3 ').astype(int)
df3['INDFMMPI'] = df2.eval('INDFMMPI < 1.0').astype(int)
 
# Exclude missing vaule
df3 = df3.dropna(axis = 0, how = 'any')
# Mask GH and METS with 0
df3.loc[:,['LBXGH', 'METS']] = 0

# Output csv_file
df3.to_csv(sys.argv[1], index=None, header = None)