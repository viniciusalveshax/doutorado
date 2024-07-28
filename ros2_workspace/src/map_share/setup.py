from setuptools import find_packages, setup

package_name = 'map_share'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vinicius',
    maintainer_email='viniciushax@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'server_first = map_share.map_server:main',
            'client = map_share.map_client:main',
            'rand_server = map_share.map_rand_server:main',
            'rand_client = map_share.map_rand_client:main',
            'publisher = map_share.map_publisher:main', #Text ok version
            'subscriber = map_share.map_subscriber:main', #Text ok version
            'server = map_share.map_share_server:main', #Pygame version
            'pygame = map_share.map_pygame_client:main', #Pygame version
        ],
    },
)
