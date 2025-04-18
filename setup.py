from setuptools import setup, find_packages

setup(
    name='whatsapp_python',
    version='0.1.0',
    author='Sarthak Lamba',
    author_email='sarthaksnh5@gmail.com',
    description='A Python package for managing WhatsApp flows.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/sarthaksnh5/whatsapp_flows',
    packages=find_packages(where="src"),  # Specify the source directory
    package_dir={"": "src"},  # Map the root package to the src directory
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'pycryptodome',  # Corrected dependency for cryptography
        'cryptography',
    ],
)