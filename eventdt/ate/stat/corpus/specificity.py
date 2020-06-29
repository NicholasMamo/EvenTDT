"""
Domain specificity is a corpus comparison approach proposed by Park et al.
The metric promotes terms that appears in the domain corpus more frequently than in general corpora:

.. math::

	specificity(w) = \\frac{p_d(w)}{p_g(w)} = \\frac{\\frac{c_d(w)}{N_d}}{\\frac{c_g(w)}{N_g}}

where :math:`w` is the word for which domain specificity is calculated.
:math:`p_d(w)` and :math:`p_g(w)` are the probabilities that the word :math:`w` appears in the domain-specific corpus :math:`d` and the general corpus :math:`g` respectively.
Domain specificity can also be expressed in terms of token frequency.
:math:`c_d(w)` and :math:`c_g(w)` are word :math:`w`'s frequency in the domain-specific corpus :math:`d` and the general corpus :math:`g` respectively.
Similarly, :math:`N_d` and :math:`N_g` are the number of words in the domain-specific corpus :math:`d` and the general corpus :math:`g` respectively.

.. note::

	Implementation based on the metric described in `An Empirical Analysis of Word Error Rate and Keyword Error Rate by Park et al. (2008) <https://www.isca-speech.org/archive/interspeech_2008/i08_2070.html>`_.
	Domain specificity was also used in the field of ATE by `Chung et al. (2003) in A Corpus Comparison Approach for Terminology Extraction <https://www.jbe-platform.com/content/journals/10.1075/term.9.2.05chu>`_, among others.
"""
