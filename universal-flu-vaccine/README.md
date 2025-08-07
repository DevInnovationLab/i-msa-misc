# universal-flu-vaccine

This folder contains code and output related to our [CGD blog post on universal flu vaccines](https://www.cgdev.org/blog/hhs-dont-put-all-your-vaccine-shots-egg-basket). The associated Google Drive folder is [here](https://drive.google.com/drive/folders/1l_tNzOyjCZHjwSIyb4T8dAfPXyqtLYS0?usp=drive_link).


## Setup

We use [poetry](https://python-poetry.org/) for package and dependency management and [pre-commit](https://pre-commit.com/) to enforce code quality.

### Poetry

Install poetry following the instructions [here](https://python-poetry.org/docs/#installation).

Create the virtual environment and initiate a fresh install of the project dependencies:
```bash
poetry install
```

To run project scripts, activate the virtual environment:
```bash
poetry shell
```

You can then run python commands as per usual.

To exit:
```bash
exit
```

To add dependencies, run:
```bash
poetry add package-name
```

To update dependencies, run:
```bash
poetry update
```

## Contributing

See instructions in the `i-msa-misc` top-level README.

