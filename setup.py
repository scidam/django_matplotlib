from setuptools import setup
import setuptools

README_FILE = 'README.rst'
with open(README_FILE, 'r', encoding='utf-8') as d:
    desc = d.read()


setup(name='django-matplotlib',
        packages=setuptools.find_packages(exclude=['docs', 'media']),
        long_description_content_type='text/x-rst',
        version='0.1',
        description='Matplotlib field for Django',
        keywords='django, matplotlib, python',
        long_description=desc,
        include_package_data=True,
        author='Dmitry Kislov',
        author_email='kislov@easydan.com',
        url='https://github.com/scidam/django_matplotlib',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Topic :: Software Development',
            'Intended Audience :: Developers'
            ],
        package_data={
        'django_matplotlib': ['templates/**/*.html',]
        },            
        python_requires='>=3.5'
      )

