from pathlib import Path
from setuptools import setup
from mindquest import __version__
from pkg_resources import parse_requirements


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='mindquest',
    version=__version__,
    url='https://github.com/dimastatz/whisper-flow',
    author='Dima Statz',
    author_email='dima.statz@gmail.com',
    py_modules=['mindquest'],
    python_requires=">=3.9",
    install_requires=[
        str(r)
        for r in parse_requirements(
            Path(__file__).with_name("requirements.txt").open()
        )
    ],
    description='mindquest: An AI-powered platform that creates fun, educational podcasts for children aged 6–12 by turning verified facts into engaging audio stories using LLMs and high-quality text-to-speech technology',
    long_description = long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    package_data={'': ['static/*']},
)