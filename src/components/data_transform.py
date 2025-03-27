import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle
import os
import boto3
from src.config import sagemaker_processing_path,dataset_name
import traceback

def data_tranform(data):
    try:
        print('data transformation start...')
        s3 = boto3.client('s3')
        bucket_name='myricebucket'
        train_key='data/train_e.csv'
        test_key='data/test_e.csv'
        transformer_key='data/preprocessor.pkl'
        
        #train_path=os.path.join('s3://myricebucket/data','train_e.csv')
        #test_path=os.path.join('s3://myricebucket/data','test_e.csv')
        #processor_path=os.path.join('/opt/ml/processing/output','preprocessor.pkl')
        
        df = pd.read_csv(data,engine='python',nrows=10)
        train_df,test_df=train_test_split(df,test_size=0.2,random_state=42,stratify=df['Class'])
        train_df.Class.replace(to_replace={'Cammeo':0,'Osmancik':1},inplace=True)
        test_df.Class.replace(to_replace={'Cammeo':0,'Osmancik':1},inplace=True)
        
        print('read and splited data sucessfully...')

        num_cols=test_df.columns.tolist()[:-1]
        num_pipeline=Pipeline(steps=[('scaling',StandardScaler())])
        transform=ColumnTransformer(transformers=[('numeric_transform',num_pipeline,num_cols)])
        
        train_transform=transform.fit_transform(train_df)

        train_encode_df=pd.DataFrame(train_transform,columns=test_df.columns.tolist()[:-1])
        #train_encode_df['Class']=train_df['Class'].tolist()
        train_encode_df.insert(0,'Class',train_df['Class'].tolist()) #adding target column as first column of the train_encode_df.
        
        test_transform=transform.transform(test_df)
        test_encode_df=pd.DataFrame(test_transform,columns=train_df.columns.tolist()[:-1])
        #test_encode_df['Class']=test_df.Class.tolist()
        test_encode_df.insert(0,'Class',test_df.Class.tolist())

        print('staring the loading process..')
        
        tr=train_encode_df.to_csv(index=False,header=False)
        te=test_encode_df.to_csv(index=False,header=False)
        trans_object=pickle.dumps(transform)
        
        s3.put_object(Bucket=bucket_name, Key=train_key, Body=tr)
        print('train load done')
        s3.put_object(Bucket=bucket_name, Key=test_key, Body=te)
        print('test load done')
        s3.put_object(Bucket=bucket_name, Key=transformer_key, Body=trans_object)
        print('pickle load done..')
        print('process completed...!')
        

        #train_encode_df.to_csv(train_path,index=False,header=False)
        #test_encode_df.to_csv(test_path,index=False,header=False)
    except Exception as e:
        print('The error ocuuren in the data transform.py : {}'.format(e))
        traceback.print_exc()

    print('data transform method execution is completed...')


if __name__=='__main__':
    input_path=os.path.join(sagemaker_processing_path,dataset_name)
    data_tranform(input_path)