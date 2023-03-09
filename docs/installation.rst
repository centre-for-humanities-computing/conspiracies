Installation
==================
To get started using this package install it using pip by running the following line in your terminal:

.. code-block:: bash

   pip install conspiracies


There should be no discrepancy between the latest version installed using pip or the version on GitHub.

To install dependencies for using the prompt relation extraction, run the following command:

.. code-block:: bash

   pip install conspiracies[openai]



Development Installation
^^^^^^^^^^^^^^^^^^^^^^^^^

To set up the development environment for this package, clone the repository and install the
package using the following commands:

.. code-block::

   git clone https://github.com/centre-for-humanities-computing/conspiracies
   cd conspiracies

   pip install -e ".[style,tests,docs,tutorials]"

Furthermore if you wants to run the tests, you will need to install the spacy
pipelines specificed in :code:`test/requirements.txt`:

.. code-block::

   pip install -r test/requirements.txt

Lastly, if you want to make sure the style format specified by the pre-commit hooks
is correct, you will need to install the pre-commit hooks:

.. code-block::

   pre-commit install

Which will run the pre-commit hooks on every commit. To run the pre-commit hooks
manually you can simply run:

.. code-block::

   pre-commit run --all-files