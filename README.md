typedload
=========

Dynamic data structures are nice, but they quickly become difficult to work
with, when more static ones are easier to work with but are awkward to use to
exchange data externally.

This is a library to load untyped data (coming from example from a json string)
and convert it into Python's NamedTuple or similar, respecting all the type
hints and performing type checks or casts when needed.

Note that it is released with a GPL license and it cannot be used inside non
GPL software.
