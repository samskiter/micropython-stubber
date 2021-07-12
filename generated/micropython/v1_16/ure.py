from typing import Any, Optional, Union, Tuple

# .. module:: ure
# origin: micropython\docs\library\ure.rst
# v1.16
"""
   :synopsis: regular expressions

|see_cpython_module| :mod:`python:re`.

This module implements regular expression operations. Regular expression
syntax supported is a subset of CPython ``re`` module (and actually is
a subset of POSIX extended regular expressions).

Supported operators and special sequences are:

``.``
   Match any character.

``[...]``
   Match set of characters. Individual characters and ranges are supported,
   including negated sets (e.g. ``[^a-c]``).

``^``
   Match the start of the string.

``$``
   Match the end of the string.

``?``
   Match zero or one of the previous sub-pattern.

``*``
   Match zero or more of the previous sub-pattern.

``+``
   Match one or more of the previous sub-pattern.

``??``
   Non-greedy version of ``?``, match zero or one, with the preference
   for zero.

``*?``
   Non-greedy version of ``*``, match zero or more, with the preference
   for the shortest match.

``+?``
   Non-greedy version of ``+``, match one or more, with the preference
   for the shortest match.

``|``
   Match either the left-hand side or the right-hand side sub-patterns of
   this operator.

``(...)``
   Grouping. Each group is capturing (a substring it captures can be accessed
   with `match.group()` method).

``\d``
   Matches digit. Equivalent to ``[0-9]``.

``\D``
   Matches non-digit. Equivalent to ``[^0-9]``.

``\s``
   Matches whitespace. Equivalent to ``[ \t-\r]``.

``\S``
   Matches non-whitespace. Equivalent to ``[^ \t-\r]``.

``\w``
   Matches "word characters" (ASCII only). Equivalent to ``[A-Za-z0-9_]``.

``\W``
   Matches non "word characters" (ASCII only). Equivalent to ``[^A-Za-z0-9_]``.

``\``
   Escape character. Any other character following the backslash, except
   for those listed above, is taken literally. For example, ``\*`` is
   equivalent to literal ``*`` (not treated as the ``*`` operator).
   Note that ``\r``, ``\n``, etc. are not handled specially, and will be
   equivalent to literal letters ``r``, ``n``, etc. Due to this, it's
   not recommended to use raw Python strings (``r""``) for regular
   expressions. For example, ``r"\r\n"`` when used as the regular
   expression is equivalent to ``"rn"``. To match CR character followed
   by LF, use ``"\r\n"``.

**NOT SUPPORTED**:

* counted repetitions (``{m,n}``)
* named groups (``(?P<name>...)``)
* non-capturing groups (``(?:...)``)
* more advanced assertions (``\b``, ``\B``)
* special character escapes like ``\r``, ``\n`` - use Python's own escaping
  instead
* etc.

Example::

    import ure

    # As ure doesn't support escapes itself, use of r"" strings is not
    # recommended.
    regex = ure.compile("[\r\n]")

    regex.split("line1\rline2\nline3\r\n")

    # Result:
    # ['line1', 'line2', 'line3', '', '']
"""
# .. function:: compile(regex_str, [flags])
def compile(regex_str, flags: Optional[Any]) -> Any:
    """
    Compile regular expression, return `regex <regex>` object.
    """
    ...


# .. function:: match(regex_str, string)
def match(regex_str, string) -> Any:
    """
    Compile *regex_str* and match against *string*. Match always happens
    from starting position in a string.
    """
    ...


# .. function:: search(regex_str, string)
def search(regex_str, string) -> Any:
    """
    Compile *regex_str* and search it in a *string*. Unlike `match`, this will search
    string for first position which matches regex (which still may be
    0 if regex is anchored).
    """
    ...


# .. function:: sub(regex_str, replace, string, count=0, flags=0, /)
def sub(regex_str, replace, string, count=0, flags=0, /) -> Any:
    """
    Compile *regex_str* and search for it in *string*, replacing all matches
    with *replace*, and returning the new string.

    *replace* can be a string or a function.  If it is a string then escape
    sequences of the form ``\<number>`` and ``\g<number>`` can be used to
    expand to the corresponding group (or an empty string for unmatched groups).
    If *replace* is a function then it must take a single argument (the match)
    and should return a replacement string.

    If *count* is specified and non-zero then substitution will stop after
    this many substitutions are made.  The *flags* argument is ignored.

    Note: availability of this function depends on :term:`MicroPython port`.
    """
    ...


# .. data:: DEBUG
# .. method:: regex.match(string)
class regex:
    """ """

    def match(self, string) -> Any:
        """
                 regex.search(string)
                 regex.sub(replace, string, count=0, flags=0, /)

        Similar to the module-level functions :meth:`match`, :meth:`search`
        and :meth:`sub`.
        Using methods is (much) more efficient if the same regex is applied to
        multiple strings.
        """
        ...

    # .. method:: regex.split(string, max_split=-1, /)
    def split(self, string, max_split=-1, /) -> Any:
        """
        Split a *string* using regex. If *max_split* is given, it specifies
        maximum number of splits to perform. Returns list of strings (there
        may be up to *max_split+1* elements if it's specified).
        """
        ...


# .. method:: match.group(index)
class match:
    """ """

    def group(self, index) -> Any:
        """
        Return matching (sub)string. *index* is 0 for entire match,
        1 and above for each capturing group. Only numeric groups are supported.
        """
        ...

    # .. method:: match.groups()
    def groups(
        self,
    ) -> Any:
        """
        Return a tuple containing all the substrings of the groups of the match.

        Note: availability of this method depends on :term:`MicroPython port`.
        """
        ...

    # .. method:: match.start([index])
    def start(self, index: Optional[Any]) -> Any:
        """
                 match.end([index])

        Return the index in the original string of the start or end of the
        substring group that was matched.  *index* defaults to the entire
        group, otherwise it will select a group.

        Note: availability of these methods depends on :term:`MicroPython port`.
        """
        ...

    # .. method:: match.span([index])
    def span(self, index: Optional[Any]) -> Any:
        """
        Returns the 2-tuple ``(match.start(index), match.end(index))``.

        Note: availability of this method depends on :term:`MicroPython port`.
        """
        ...
