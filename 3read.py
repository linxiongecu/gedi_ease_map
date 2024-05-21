import geopandas as pd
######   pip install pyarrow
df=pd.read_parquet('tiles.parquet')
print(df.columns)
print(df)
