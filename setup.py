from setuptools import setup, find_packages

setup(
    name="WebPilot",
    version="0.1.0",
    description="Controlling the web - redefined",
    author="Amit Nakash",
    author_email="amit.nakash.biz@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "loguru>=0.6.0,<1.0.0",
        "fastapi>=0.109.1,<0.110.0",
        "black>=24.3.0,<25.0.0",
        "pydantic>=2.10.6",
        "pydantic-settings>=2.8.1" "pyppeteer>=1.0.2,<2.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "uvicorn>=0.23.2,<1.0.0",
        "cachetools>=5.3.3,<6.0.0",
        "fake-useragent>=1.5.1,<2.0.0",
        "uvloop>=0.21.0,<1.0.0",
        "redis>=5.2.0,<6.0.0",
        "psutil>=6.1.0,<7.0.0",
        "nanoid>=2.0.0,<3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.2,<8.0.0",
            "pytest-asyncio>=0.21.1,<1.0.0",
            "pytest-mock>=3.12.0,<4.0.0",
        ],
    },
    python_requires=">=3.12",
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: MIT License",
        "Operating System :: OS Independent",
    ],
)
