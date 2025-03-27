# Project Brief:

**This is an end-to-end ML project, which demonstrate mainly on the life cycle of ML project and deployment with principles of CI/CD in AWS.**

## Steps to run the project using codeCommit, codeBuild, codeDeploy and codePipeline:

1. Create on remote repository i,e a repository in codeCommit eg:rice-project.  
2. After all validations, push the correct/running code from your local working repository to remote repository which we created in the step-1.
3. Create one s3 bucket to save your files, artifacts and all eg:rice-bucket.
4. Create one ECR repository to save your docker images which we are building and pushing during build process i,e step-5.
5. Go to codeBuild service and create one build project eg:rice-build, and assign the required roles and permissions to the created build project as per your need. In this current project my script need data from s3 bucket, need resources from sagemaker and ECR for pushing docker images, so i assign the(CodeBuildBasePolicy-simple-us-east-1, AmazonS3FullAccess, AmazonSageMakerFullAccess, rice-ecr-access-> this is inline policy created for ECR access, in this policy you need to add your ECR repository ARN). Also make sure that, when you are using sagemaker resources in your project/script add the sagemaker.com service under the trust-relationship section of your build project.
6. After successfully running the build project, save the artifacts/app-revison to the s3 bucket which we created in the step-3, to happen the step-5, you can enable the option saving artifacts in s3 bucket while you creating the build project in step-4.
7. Once your aritifacts/app-revision is saved in your s3 bucket, go to the EC2 service and create instances as per your need and assign the required role and permissions. In this project my EC2 instances access s3 bucket for aritfacts/app-revision, access ECR for latest docker images and also sagemaker for using endpoints, so i assign the(AmazonEC2ContainerRegistryFullAccess, AmazonS3ReadOnlyAccess, Edpoint-invoke-> this is inline policy created for Invoking the enpoints in sagemaker).
8. After creating the EC2 instance, make sure to install codeDeploy-agent and all other required thing for deployment. In this project i used docker, so i installed docker on all EC2 instances.
9. After setup the EC2 instances, go to codeDeploy service and create one application eg:rice-app, in that application create one deployment group eg:dev-deploy, and assign the required roles and permisssions. In this current project i assigned this role(AWSCodeDeployRole) for deployment purpose. Once after setup the codeDeploy, just go to deployment group and start the deployment.
10. After testing and validation of your application with codeBuild and codeDeploy, to make your follow the principles of CI/CD use the codePipeline service in AWS. Go to codePipeline service and create one pipeline using data, inputs and artifacts from the previously used service "codeCommit, codeBuild and codeDeploy". And if you want to add the manual approval step in your pipeline, go to SNS service and create one topic with protocol "Email". After creating the SNS topic, add the new stage(manual-approval) in pipeline and in that stage create one action group, in that group provide the ARN of the SNS which we created earlier and save the changes and trigger the pipeline. 

## Important and useful note on Docker :

**Docker setup on EC2 instance :**

sudo yum update -y  
sudo yum install docker (enter y  if it ask any)  
docker --version  
sudo systemctl start docker  
sudo systemctl enable docker  
sudo usermod -aG docker ec2-user  
exit  
groups  
docker ps or docker info.  

**Docker container useful commands :**

1. docker exec -it <container_id> ls /usr/src/app - used to list the files inside the container.
    >Eg : docker exec -it 5d2326a4a4cb ls

2. docker exec -it <container_id> /bin/bash - used to enter inside the container file system.
    >Eg: docker exec -it 5d2326a4a4cb /bin/bash

**should I need to install requirements.txt first or build the custom packages first in docker file?**

The order of operations in your Dockerfile depends on your specific requirements and project structure. Typically, you'll want to install dependencies before building and installing custom packages. Here's why:  
1. Install Dependencies First:
    * Installing dependencies listed in requirements.txt ensures that all required libraries and packages are available in the container environment.
    * This step ensures that your custom packages can be built and installed successfully without missing dependencies.
2. Build Custom Packages Second:
    * After installing dependencies, you can proceed to build and install your custom packages.
    * Building custom packages may depend on the installed dependencies, so it's essential to have them available beforehand.

**To run the particular docker file in the project use the flag -f I,e**
1. Let's say if my project has two docker file (Dockerfile.preprocess, Dockerfile.app) and if you want to run Dockerfile.app then use the below mentioned commands.
    >docker build -f <docker_file_name> -t <name_for_the_current_bulding_image> eg: docker build -f Dockerfile.app -t my_app .
2. To run the above builded docker image as containerized application use the below command.
    >docker run -d -p 8080:8080 my_app:latest

## Important and useful note on codeBuild :

**Trust relationship :**
1. when we running our python script using codeBuild build project, and in your script if you are using sagemaker, then you need make sure that, the sagemaker to assume the IAM role used in build  project. To do this, we need to add sagemaker as trust relationship in the IAM role we used in our build project I,e  

2. Add the below code under the  trust relationship section of IAM role which we used in our build project :  
    '''
    {
    "Effect": "Allow",
    "Principal": {
        "Service": "sagemaker.amazonaws.com"
    },
    "Action": "sts:AssumeRole"
    }
    '''

**Which base image need to use in Docker file for sagemaker processing job?**

1. When you run your preprocessing script using sagemaker processing container, with the help of docker file, then you must and should make sure that the base image architecture your using in docker file and sagemaker instance architecture  should be same I,e 

2. For example :
    >If the sagemaker processing instance architecture : x86_64, then you need you use same python base image which supports x86_64 architecture in docker file I,e below line of the statement.
3. Use the official Python 3.11 slim image for x86_64 architecture
    >FROM python:3.11-slim

## Code-deploy agent installation on EC2 instance:

sudo yum update -y  
sudo yum install -y ruby  
sudo yum install -y wget  
wget https://aws-codedeploy-ap-south-1.s3.ap-south-1.amazonaws.com/latest/install  
chmod +x ./install  
sudo ./install auto  
sudo service codedeploy-agent status  

#If error  
sudo service codedeploy-agent start  
sudo service codedeploy-agent status

## Best paractices for new projects :

1. Create one new directory for the project in local system, and create one separate anaconda environment for effectively managing the packages/modules and files in new project.
2. For creating new anaconda environment, use the below command.
    > conda create --name myenv python=3.8, eg: conda create --name myriceenv python=3.11.7
3. List of usefull commands :  
     **Create a new environment with Python 3.8**  
    conda create --name data_science python=3.8

    **Activate the new environment**  
    conda activate data_science

    **Install some packages**  
    conda install numpy pandas matplotlib scikit-learn

    **Verify the environment**  
    conda list

    **Deactivate the environment**  
    conda deactivate

    **To list all your conda environments**  
    conda env list

## Important and usefull note on building custom packages :

1. Make sure to have the "__init__.py" file in your sub-directories, which helps to find_packages() function in setup.py to treat your sub-directories as packages.
2. After creating your sub-directories/custom-packages for your project, to build the custom-packages runt the command "pip install ."
3. Make sure, before running "pip install ." run the requirements.txt. I,e "pip install -r requirements.txt".
