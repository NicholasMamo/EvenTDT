"""
The log-likelihood ratio compares the observed co-occurrence of terms with their expected co-occurrence.
The expected co-occurrence, or the null hypothesis, is the number of times two terms appear if they were independent of each other.

The log-likelihood ratio is calculated as follows:

.. math::

	-2ln(\\lambda) = 2 \\cdot O ln(\\frac{O}{E})

where :math:`E` is the expected number of co-occurrences of two terms and :math:`O` is the actual number of observed co-occurrences.
The :math:`O` before the logarithm boosts common terms.

With this equation:

- Terms that appear more often than expected (that is, they are not independent) will have a positive logarithm;
- Terms that appear as often as expected (that is, they are independent) will have a logarithm of 0; and
- Terms that appear less often as expected (that is, they are negatively correlated), will have a negative logarithm.

To calculate the log-likelihood ratio, this algorithm uses a contingency table:

+-------------------------+-------------------------+-------------------------+
|                         || :math:`t_1`            | :math:`\\overline{t_1}`  |
+=========================+=========================+=========================+
| :math:`t_2`             || A                      | B                       |
+-------------------------+-------------------------+-------------------------+
| :math:`\\overline{t_2}`  || C                      | D                       |
+-------------------------+-------------------------+-------------------------+

In this table, the cells represent the following:

- `A`: terms :math:`t_1` and :math:`t_2` co-occur;
- `B`: terms :math:`t_2` appears, but :math:`t_1` doesn't;
- `C`: terms :math:`t_1` appears, but :math:`t_2` doesn't; and
- `D`: neither terms :math:`t_1` nor :math:`t_2` appear.
"""
