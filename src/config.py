pre_processor='src/components/data_transform.py'
sagemaker_processing_path='/opt/ml/processing/input'
dataset_name='dataset.csv'
train_file='s3://myricebucket/data/train_e.csv'
test_file='s3://myricebucket/data/test_e.csv'
model_output='s3://myricebucket/data/output'
role="arn:aws:iam::590183891223:role/service-role/codebuild-simple-service-role"
dataset_path='s3://myricebucket/data/dataset.csv'
