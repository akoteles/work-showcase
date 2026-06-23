from setuptools import setup

setup(
    use_scm_version=True,
    name="pipeline_fw_files",
    author="ClientAuto PIPELINE_FW Team",
    author_email="pipeline_fw@list.internal.example.com",
    package_dir={
        "pipeline_fw_files_phase1": "src/phase1",
        "pipeline_fw_files_phase2": "src/phase2",
    },
    packages=["pipeline_fw_files_phase1", "pipeline_fw_files_phase2"],
    setup_requires=["pytest-runner", "setuptools_scm"],
    install_requires=[
        "boto3",
        "paramiko",
        "cdh-lambda@git+ssh://git@git.example.com:7999/cdh/cdh-lambda-lib.git@abc123def456abc123def456abc123def456abc1#egg=cdh-lambda",
    ],
    tests_require=["pytest"],
)
