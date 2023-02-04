# set up the environment
# assumes you are in a virtualenv

PROJECT_DIR="./"

# Change dir
cd $PROJECT_DIR

# install the package and test requirements
pip install -e ".[tutorials,style,tests,docs]"; pip install -r tests/requirements.txt

# setup pre commit hooks
pre-commit install