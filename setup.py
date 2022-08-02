"""安装启动文件"""

from setuptools import setup

setup(
    name='piz-base-py',
    version='1.0.0',
    description='pizazz-python',
    license='MIT',
    author='pizazz',
    author_email='',
    platforms='any',
    include_package_data=True,
    packages=[
        'piz_base',
        'piz_base.common',
        'piz_base.tool',
        'piz_component',
        'piz_component.kafka',
        'piz_component.kafka.resource',
        'piz_component.kafka.consumer',
        'piz_component.kafka.producer',
        'piz_component.redis'
    ],
    package_data={
        'piz_component.kafka.resource': [
            'piz_component/kafka/resource/*.yml'
        ]
    },
    install_requires=[
        'kafka-python>=2.0.2',
        'redis>=4.3.4',
        'pyyaml>=6.0',
        'python-dateutil>=2.8.2'
    ],
    zip_safe=False)
