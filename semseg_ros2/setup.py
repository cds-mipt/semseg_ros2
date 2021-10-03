from setuptools import setup

package_name = 'semseg_ros2'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='docker_semseg',
    maintainer_email='docker_semseg@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'semseg_node = semseg_ros2.semseg_node:main',
            'visualizer_node = semseg_ros2.visualizer_node:main'
        ],
    },
)
