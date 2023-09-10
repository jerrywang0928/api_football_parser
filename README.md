websit: https://rapidapi.com/api-sports/api/api-football
<img width="1153" alt="Screenshot 2023-09-10 at 5 11 37 PM" src="https://github.com/jerrywang0928/api_football_parser/assets/77896133/d69eaab8-f44f-4554-91cc-f3809fb3f559">

PyPI Login: https://pypi.org/account/login/
UserName: zw2888

[metadata]
name = apollov2_api_parser
version = 0.0.1
author = zhe wang
description = extract data from api and transform it into dataframe
long_description = file: README.md
long_description_content_type = text/markdown
classifiers =
    Programming Language :: Python :: 3
    License :: OSI Approved :: MIT License
    Operating System :: OS Independent


[options]
package_dir =
    = src
packages = find:
python_requires = >=3.6

[options.packages.find]
where = src

 
To publish your own package in Python, you need to follow these steps or watch this vedio https://www.youtube.com/watch?v=v4bkJef4W94:

1. **Structure Your Project:** A typical Python project's structure looks something like this:

    ```
    project_dir/
        package_dir/
            __init__.py
            module1.py
            module2.py
        setup.py
        README.md
        LICENSE.txt
    ```
    `project_dir/` is the root directory of your project.

    `package_dir/` is the directory containing your Python code. You can have multiple modules in your package. 

    `setup.py` is the build script for setuptools. It tells setuptools about your package (such as the name and version) as well as files to include.

    `README.md` provides a detailed description of the project.

    `LICENSE.txt` is the license for your project, which determines how it can be used by others.

2. **Create `setup.py`:** This file tells setuptools about your package. A minimal setup.py file could look something like this:

    ```python
    from setuptools import setup, find_packages

    setup(
        name="Your-Package-Name",
        version="0.1",
        packages=find_packages(),
    )
    ```
    For more complex packages, you can specify additional metadata such as a project description, author, license, etc.

3. **Generate `dist/`:** Now that your project is structured correctly and setup.py is ready, you can generate distribution packages for your project. These are archives that are uploaded to the Package Index and can be installed by pip. Run the following command:

    ```bash
    python setup.py sdist bdist_wheel
    ```

4. **Install `twine`:** `twine` is a utility for publishing Python packages on PyPI. You can install it with pip:

    ```bash
    pip install twine
    ```

5. **Publish Your Package:** Now that you have generated the distribution archives, you can publish them to PyPI. Use `twine` to upload your distribution archives:

    ```bash
    twine upload dist/*
    ```

    You'll be prompted to provide your PyPI username and password. If you don't have a PyPI account, you need to create one. 

6. **Install and Test Your Package:** Now that the package is published, anyone can install it with pip:

    ```bash
    pip install Your-Package-Name
    ```

Please, replace `"Your-Package-Name"` with the actual name of your package.

Remember to follow Python's guide on packaging projects and PyPI's guide on distribution for detailed instructions and best practices.
