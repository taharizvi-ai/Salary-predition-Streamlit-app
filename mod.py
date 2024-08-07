import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
import pickle

# Define functions for data processing and model training
def readDf(path):
    df = pd.read_csv(path)
    df = df.drop(columns=['FIRST NAME', 'LAST NAME'])
    df = df.dropna()
    return df

def typeCast(df):
    df['DOJ'] = pd.to_datetime(df['DOJ'])
    df['CURRENT DATE'] = pd.to_datetime(df['CURRENT DATE'])
    return df

def featTar(df):
    X = df.drop(columns=['SALARY'])
    y = df['SALARY']
    return X, y

def split_(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

def featEng(X_train, X_test):
    X_train['SERVICE'] = (X_train['CURRENT DATE'] - X_train['DOJ']).dt.days
    X_test['SERVICE'] = (X_test['CURRENT DATE'] - X_test['DOJ']).dt.days
    X_train = X_train.drop(columns=['CURRENT DATE', 'DOJ'])
    X_test = X_test.drop(columns=['CURRENT DATE', 'DOJ'])
    return X_train, X_test

def encode(X_train, X_test):
    s = (X_train.dtypes == 'object')
    object_cols = list(s[s].index)

    OH_encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)
    OH_cols_train = pd.DataFrame(OH_encoder.fit_transform(X_train[object_cols]))
    OH_cols_valid = pd.DataFrame(OH_encoder.transform(X_test[object_cols]))

    OH_cols_train.index = X_train.index
    OH_cols_valid.index = X_test.index

    num_X_train = X_train.drop(object_cols, axis=1)
    num_X_test = X_test.drop(object_cols, axis=1)

    OH_X_train = pd.concat([num_X_train, OH_cols_train], axis=1)
    OH_X_test = pd.concat([num_X_test, OH_cols_valid], axis=1)

    OH_X_train.columns = OH_X_train.columns.astype(str)
    OH_X_test.columns = OH_X_test.columns.astype(str)

    return OH_X_train, OH_X_test, OH_encoder

def train_model(OH_X_train, y_train):
    model = RandomForestRegressor(n_estimators=100, random_state=0)
    model.fit(OH_X_train, y_train)
    return model

# Retrain and save the model
if __name__ == "__main__":
    path = 'Salary Prediction of Data Professions.csv'
    X, y = featTar(typeCast(readDf(path)))
    X_train, X_test, y_train, y_test = split_(X, y)
    X_train, X_test = featEng(X_train, X_test)
    OH_X_train, OH_X_test, encoder = encode(X_train, X_test)

    with open('encoder.pkl', 'wb') as f:
        pickle.dump(encoder, f)
    model = train_model(OH_X_train, y_train)
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)

    preds = model.predict(OH_X_test)
    print(f"Sample prediction: {preds[0]}")
