import pandas as pd
import numpy as np

df=pd.read_csv('Zomato_Dataset.csv')


df['cost_per_person']=df['Average_Cost_for_two']/2
df = df[df['cost_per_person'] > 0]
print(df.head(5))

def cost_category(cost):
  if cost<300:
    return 'Low'
  elif cost<700:
    return 'Medium'
  else:
    return 'High'
df['cost_category']=df['cost_per_person'].apply(cost_category)
print(df.head(5))
df['Cuisines'] = df['Cuisines'].fillna("Unknown")
df['num_cuisines']=df['Cuisines'].apply(lambda x: len(x.split(',')))
df['primary_cuisines']=df['Cuisines'].apply(lambda x: x.split(',')[0])

df['Has_Online_delivery']=df['Has_Online_delivery'].map({0:'No',1:'Yes'})
df['Has_Table_booking']=df['Has_Table_booking'].map({0:'No',1:'Yes'})

def rating_bucket(x):
  if x>4.5:
    return 'Excellent'
  elif x>3.5:
    return 'Good'
  elif x>2.5:
    return 'Average'
  else:
    return 'Poor'

df['Rating_Bucket']=df['Rating'].apply(rating_bucket)

df['log_votes']=np.log1p(df['Votes'])

df['popularity_score']=df['Rating']*df['Votes']

df['Value-for-money']=(df['Rating']/df['cost_per_person']+1)

city_counts = df['City'].value_counts().to_dict()
df['city_competition'] = df['City'].map(city_counts)

print(df['Currency'].nunique())

df = df.drop(columns=[
    'Address',
    'Locality',
    'LocalityVerbose',
    'Switch_to_order_menu'
])

df['city_competition_norm'] = df['city_competition'] / df['city_competition'].max()
# print(df.head(5))

# print(df.isnull().sum())

print(df.describe())

df.to_csv('Cleaned_Zomato_Dataset.csv', index=False)
