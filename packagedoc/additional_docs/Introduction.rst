The Python package ``GenPackageDoc`` generates the documentation of Python modules. The content of this documentation is taken out of the docstrings of
functions, classes and their methods.

It is possible to extend the documentation by the content of additional text files. The docstrings and also the
additional text files have to be written in rst syntax (rst is the abbreviation for "**r**\ e **s**\ tructured **t**\ ext",
that is a certain markdown dialect).

The documentation is generated in two steps:

1. The rst sources are converted into LaTeX sources
2. The LaTeX sources are converted into a PDF document. This requires a separately installed LaTeX distribution (recommended: MiKTeX),
   that is **not** part of ``GenPackageDoc``.

The sources of ``GenPackageDoc`` are available in the following GitHub repository (*soon*):

   https://github.com/test-fullautomation/python-genpackagedoc

The repository ``python-genpackagedoc`` uses it's own functionality to document itself and the contained Python package ``GenPackageDoc``.
Therefore the complete repository can be used as an example to learn how to write a documentation.

Currently no ``setup.py`` is available. Later this setup script will install some libraries of ``GenPackageDoc``. As long as there are no libraries installed,
the local version within this repository are used for documentation build.

But independend from such installations it has to be considered, that the main goal of ``GenPackageDoc`` is to document Python sources that are stored
within a repository, and therefore we have dependencies to the structure of the repository. For example: Configuration files with values
that are specific for a repository, should not be installed. Such a specific configuration value is e.g. the name of the package or the name of the PDF document.

The impact is: There is a deep relationship between the repository containing the sources to be documented, and the sources and the configuration
of ``GenPackageDoc`` itself. Therefore some manual preparations are necessary to use ``GenPackageDoc`` also in every other repository.

How to do this is explained in detail in the next chapters.

The outcome of all preparations of ``GenPackageDoc`` in your own repository is a PDF document like the one you are currently reading.
