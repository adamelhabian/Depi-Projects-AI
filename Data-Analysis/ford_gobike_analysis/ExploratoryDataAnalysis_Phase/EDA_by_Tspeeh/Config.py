import pandas as pd
def Read_data_file(file_path):
    df=pd.read_csv(file_path)
    return df
def Drop_unnecessary_features(df, cols_to_drop):
    df.drop(columns=cols_to_drop,inplace=True)
    return df
def Check_data_type(df):
    report = pd.DataFrame({
        "Data Type": df.dtypes,
        "Unique Values": df.nunique()
    })
    return report.T
def convert_datatypes_categorical(df, Cols_to_convert):
    df[Cols_to_convert] = df[Cols_to_convert].astype("category")
    return Check_data_type(df)
def Show_missing_Data(df):
    return  df.isnull().sum()
def Get_med(df,essCol):
    med=df[essCol].median()
    return med
def Fill_Nulls(df,nullValCol,medVal):
    df[nullValCol] = df[nullValCol].fillna(medVal)
    return df
def Avg_Ages(df,col):
    avg=df[col].mean()
    return avg