import pandas as pd
from sklearn.metrics import confusion_matrix
#%%
df=pd.read_csv(r'C:\Users\adaml\Python\Fairness Systems\combined.csv')
print(df.head())
cm = confusion_matrix(list(df['income']), list(df['predicted income']), labels=df['income'].unique())
print(cm)



# %%
