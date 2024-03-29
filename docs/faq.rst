Frequently asked questions
================================


How do I run the pipeline?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have installed the package, you can run the pipeline via :code:`conspiracies.run`.

.. code-block:: bash

   python3 -m conspiracies.run my_project_name my_input_path


For fine-grained control of pipeline behavior, create a configuration file based on the `config template <https://github.com/centre-for-humanities-computing/conspiracies/blob/main/config/template.toml>`__.  and
pass it with the :code:`-c` flag.


.. code-block:: bash

   python3 -m conspiracies.run my_project_name my_input_path -c my-config.toml


Project name and input path can also be specified in the configuration instead in which
case you can do

.. code-block:: bash

   python3 run.py -c config/my-config.toml

If you have installed the package and want to integrate (parts of) the
pipeline into your own workflow, you can use individual components or integrate a
:code:`Pipeline` object in your script.


How do I test the code and run the test suite?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This package comes with an extensive test suite. In order to run the tests,
you'll usually want to clone the repository and build the package from the
source. This will also install the required development dependencies
and test utilities defined in the extras_require section of the :code:`pyproject.toml`.

.. code-block:: bash

   pip install -e ".[tests]"

   python -m pytest


which will run all the test in the `tests` folder.

Specific tests can be run using:

.. code-block:: bash

   python -m pytest tests/desired_test.py


If you want to check code coverage you can run the following:

.. code-block::

   python -m pytest --cov=.

Does this package run on X?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This package is intended to run on all major OS, this includes Windows (latest version), MacOS (latest) and the latest version of Linux (Ubuntu). 
Similarly it also tested on python 3.8, and 3.9.
Please note these are only the systems this package is being actively tested on, if you run on a similar system (e.g. an earlier version of Linux) this package
will likely run there as well, if not please create an issue.



How is the documentation generated?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This package uses `sphinx <https://www.sphinx-doc.org/en/master/index.html>`__ to generate
documentation. It uses the `Furo <https://github.com/pradyunsg/furo>`__ theme
with custom styling.

To make the documentation you can run:

.. code-block:: bash

   # install sphinx, themes and extensions
   pip install -e ".[docs]"

   # generate html from documentations

   make -C docs html
