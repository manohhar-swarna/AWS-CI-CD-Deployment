import sagemaker
from sagemaker.session import TrainingInput
from datetime import datetime
from src.config import dataset_path,sagemaker_processing_path,role,pre_processor,model_output,train_file,test_file
from sagemaker.processing import ProcessingInput,ProcessingOutput
from sagemaker.sklearn.processing import SKLearnProcessor
#from config import sagemaker_processing_path,dataset_name
from src.logger import logging
import boto3
from datetime import datetime
import traceback
import os

def start_Build():
    #image_of_model=None
    #name_of_train_job=None
    try:
        # Set up SageMaker session and role
        sagemaker_session = sagemaker.Session()
        sgmkr_clnt = boto3.client("sagemaker")
        #this line of statement would use when we use the sagemaker notbook instance
        #role = sagemaker.get_execution_role()
        # Define SKLearnProcessor
        print('-'*80)
        print(role)
        print('-'*80)
        sklearn_processor = SKLearnProcessor(
            framework_version='0.23-1',
            role=role,
            instance_type='ml.t3.medium',
            instance_count=1
        )
        sklearn_processor.image_uri=f"590183891223.dkr.ecr.us-east-1.amazonaws.com/rice-preprocess:latest"

        print('starting the data processing job...')

        sklearn_processor.run(
            code=pre_processor,
        inputs=[ProcessingInput(
            source=dataset_path,
            destination=sagemaker_processing_path
        )])

        print('data processing job done and starting the model training...')

        region=sagemaker_session.boto_region_name
        model_img=sagemaker.image_uris.retrieve("xgboost", region, "latest")
        
        print(model_img)

        xgb_model = sagemaker.estimator.Estimator(
        image_uri=model_img,
        role=role,
        instance_count=1,
        instance_type="ml.m4.xlarge",
        output_path=model_output,
        sagemaker_session=sagemaker_session,
        volume_size=2,
        target='Class')
        
        print(xgb_model)
        
        xgb_model.set_hyperparameters(max_depth=5, num_round=5, objective="binary:logistic")

        train_ip = TrainingInput(train_file, content_type="csv")
        test_ip = TrainingInput(test_file, content_type="csv")
        now = datetime.now()
        #current_time = now.strftime("%H:%M:%S")
        #print('-'*80)
        #print("Current Time when starting training job:", current_time)
        #print('-'*80)
        
        xgb_model.fit({"train": train_ip, "validation": test_ip}, wait=True)
        
        # Wait for the training job to complete
        xgb_model.latest_training_job.wait(logs=True)
        
        training_job_description = sgmkr_clnt.describe_training_job(TrainingJobName=xgb_model.latest_training_job.name)
        training_status = training_job_description['TrainingJobStatus']

        if(training_status == "Completed"):
            key_list=[]
            s3 = boto3.client('s3')
            endpoint_key='data/current_endpoint.txt'
            bucket_name='myricebucket'
            print('model training completed and starting the endpoint creation...')
    
            model_name = "rice-xgboost-" + datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
            print(model_name)
    
        
            model_path='s3://myricebucket/data/output/{}/output/model.tar.gz'.format(xgb_model.latest_training_job.name)
            print(model_path)
    
            response = sgmkr_clnt.create_model(
            ModelName=model_name,
            PrimaryContainer={"Image": model_img, "ModelDataUrl": model_path},
            ExecutionRoleArn=role,
            )
            
            print(response)
            print('created the model for endpoint..')
    
            ep_config_name = f"rice-endpoint-config-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
            
            print(ep_config_name)
    
            response = sgmkr_clnt.create_endpoint_config(
            EndpointConfigName=ep_config_name,
            ProductionVariants=[
            {
                "VariantName": "version-1",
                "ModelName": model_name,
                "InitialInstanceCount": 1,
                "InstanceType": "ml.m4.xlarge",
                # sever_less = ''
            }])
            
            print(response)
            print('endpoint config created...')
    
            ep_name = f"rice-endpoint-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
            
            print(ep_name)
    
            response = sgmkr_clnt.create_endpoint(
            EndpointName=ep_name, EndpointConfigName=ep_config_name)
            
            print(response)
            print('endpoint created sucessfully...')
    
            waiter = sgmkr_clnt.get_waiter("endpoint_in_service")
            waiter.wait(EndpointName=ep_name, WaiterConfig={"Delay": 123, "MaxAttempts": 123})
            
            print("Endpoint in active state...")
    
            with open('current_endpoint_name.txt','wb') as fp:
                fp.write(ep_name.encode('utf-8'))
                print('sucessfully loaded the new enpoint name in file(current_endpoint_name.txt) and location:{}'.format(os.getcwd()))
            
            print('-'*80)
            print('checking and delete any previously created endpoints...')
            print('-'*80)
            
            bucket_list_response=s3.list_objects_v2(Bucket=bucket_name)
            for i in bucket_list_response['Contents']:
                key_list.append(i['Key'])
            try:
                if(endpoint_key in key_list):
                    data_response=s3.get_object(Bucket=bucket_name, Key=endpoint_key)
                    endpoint_name=data_response['Body'].read().decode('utf-8')
                    sgmkr_clnt.delete_endpoint(EndpointName=endpoint_name)
                    print('Successfully deleted the old endpoint : {}'.format(endpoint_name))
            except Exception as e:
                print('-'*80)
                print('error related to deletion endpoint if block : {}'.format(e))
            s3.put_object(Bucket=bucket_name,Key=endpoint_key,Body=ep_name)
        else:
            print("Training job failed with status:{}".format(training_status))
            
    except Exception as e:
        #image_of_model=0
        #name_of_train_job=0
        print('-'*80)
        print('The error in data_ingestion.py {}'.format(e))
        print('-'*80)
        traceback.print_exc()
        print('-'*80)
        #return image_of_model,name_of_train_job
    #now = datetime.now()
    #current_time = now.strftime("%H:%M:%S")
    #print('-'*80)
    #print("Current Time when training job completed:", current_time)
    #print('-'*80)
    #image_of_model=model_img
    #name_of_train_job=xgb_model.latest_training_job.name
    print('data ingestion.py file execution is completed...')
    #return image_of_model,name_of_train_job
if __name__=='__main__':
    print('starting build...')
    start_Build()