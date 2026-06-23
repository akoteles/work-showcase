from setuptools import setup

setup(
    name="cdh_glue_prepared",
    description='Reusable module for creating prepared layers in ClientAuto Cloud Data Hub',
    url='https://internal.example.com/bitbucket/projects/client_pipeline/repos/cdec-glue-prepared-blueprint/browse',
    use_scm_version={
        'root': '..',
    },
    author='client_pipeline Team',
    author_email='etl_user@internal.example.com',
    packages=['cdh_glue_prepared'],
    install_requires=['pyspark==2.4.3', 'boto3'],
    setup_requires=['pytest-runner', 'setuptools_scm'],
    tests_require=['pytest', 'mock', 'pyspark-stubs~=2.4.0'],
    zip_safe=False
)
