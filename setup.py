from setuptools import setup, find_packages


setup(
    name="wsbdiscordbot",
    version="1.0",
    packages=find_packages("wsbdiscordbot", exclude=['test', 'cache']),
    install_requires=list(open('requirements.txt').readlines()),
    extras_require={
        'dev': [
            'pytest',
            'alchemy-mock'
        ],
    },
    package_dir={
        "":  "wsbdiscordbot"
    },
    package_data={
        # If any package contains these files, include them:
        "": ["*.csv", "*.json"],
    },
    entry_points={
        "console_scripts": [
            "wdbdiscordbot = wdbdiscordbot.__main__:main",
        ],
    },
)