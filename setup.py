"""安装启动文件"""

from setuptools import setup

setup(
	name='pizazz',
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
        'kafka-python>=1.4.4',
        'redis>=3.2.0',
        'uri>=2.0.1',
        'pyyaml>=5.1',
        'python-dateutil>=2.8.0',
        'redis-py-cluster>=2.1.0'
	],
    zip_safe=False)