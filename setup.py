from setuptools import find_packages, setup

with open("requirements.txt") as f:
    install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="haulage_mgmt",
    version="0.1.30",
    description="Haulage / fleet logistics for ERPNext",
    author="Haulage Mgmt",
    author_email="",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    package_data={"haulage_mgmt": ["**/*.json", "**/*.js", "**/*.html", "**/*.css", "**/*.svg", "translations/*.csv"]},
)
