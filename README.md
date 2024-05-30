# Roastery

Roastery is a framework for effectively working with the Beancount plain text
accounting software.

## Features

- **Import transactions in bulk** &mdash; Easily add new transaction
  information in bulk from data provided by your financial institutions.
- **Polished workflow for manual edits** &mdash; Is the data from your bank a
  mess? Easily classify your transactions and clean up your transaction data
  with a set of CLI tools that are optimized for speed.
- **Automate data clean up and classification** &mdash; Getting tired of making
  the same edits by hand? Write rules in Python to automatically classify and
  clean up transaction data.
- **Plays nice with version control** &mdash; Edit one of your automatic rules?
  Re-run your imports, and see the effect with a `git diff`. Manual edits are
  stored separately from original data, and the generated beancount files, so
  you can always re-run your imports.

## Project status

Roastery is a personal project without stability promise or guarantees and
warranty of any kind. I reserve the right to make breaking changes and
drastically overhaul the project without notice.

Over time, I things to stabilize and will update this notice accordingly.

<!-- end-include-doc-landing -->

## Installation

```
$ pip install roastery
```

## Contributing

Bug reports, bug fixes, and comments on the documentation are very welcome.

I am not sure if I want to take code contributions for new features at the
moment. Please reach out before you spend a lot of time on something.

## Documentation

Roastery comes with a well-documented Python API and getting started guide that
you can view at: https://roastery.duijf.io
