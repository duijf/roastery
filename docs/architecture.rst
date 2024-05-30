Architecture
============

This page documents Roastery's architecture.

Roastery is a Python library
----------------------------

The primary way of using Roastery is through a Python API. You can install
``roastery`` into a virtualenv (or similar) and then ``import roastery`` as a
Python library.

All functionality in ``roastery`` is accessed through this Python API. This means
that you can configure ``roastery`` through code and call it's functionality in a
very similar way as you can do with beancount itself.

.. note::

  If you dive into the Python API directly, you may get overwhelmed.

  Read :doc:`/getting-started/index` for a gentle introduction to Roastery.

Import
------

The Roastery import process turns statement information from you bank /
financial instituation into beancount ledger files.

The import process works in three stages:

1. **Read source format** --- Convert the original statement files from your
   financial institution into an intermediate transaction format.
2. **Clean up** --- Classify transactions. Clean up information such as payees
   and narration. This happens through either manual classification or automatic
   rules that can be programmed by the user.
3. **Write to disk** --- Data files are written to disk as beancount ledger
   files.

See also :doc:`/api/importer`.

Clean up
--------

Without further configuration, Roastery will not perform any clean up on
your transaction data. Transactions from your statements keep their original
descriptions and metadata, and are either classified as ``Income:Unknown`` or
``Expenses:Unknown``.

Roastery provides two methods to clean up transaction data:

- **Manual cleanup** --- Roastery provides CLI utility that will allow you
  to clean up every transaction in `Income:Unknown` and `Expenses:Unknown`.
- **Automatic cleanup** --- Users can also write rules in Python to
  automatically clean up and classify transactions.

.. tip::

   Attempting to automate all manual cleanup / classification has deminishing
   returns. You will likely end up with a large amount of one-off rules. Prefer to
   use Roastery's CLI utilities instead.

Advice: start by manually cleaning your transactions. This isn't as tedious as
you may think if you use the CLI utilities from Roastery. Write rules to
automate cleanup once you find yourself repeatedly performing the same bit of
clean up.
