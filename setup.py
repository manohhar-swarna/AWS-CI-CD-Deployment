from setuptools import setup, find_packages

def get_requirements(file_path):
    '''
    this function will return the list of requirements
    '''
    requirements=[]
    with open(file_path) as file_obj:
        requirements=file_obj.readlines()
        requirements=[req.replace("\n","") for req in requirements]
    return requirements

setup(
name='rice_project',
version='1.0',
author='Manu',
author_email='manohharswarnaus@gmail.com',
packages=find_packages(),
install_requires=get_requirements('requirements.txt')

)