# Uni-Haifa-214.4312-Code
Explanations, Examples, and Activities for course "Machine Learning under Uncertainty"

## Sources

- Berger, James O., 1985, Statistical Decision Theory and Statistical Analysis.

## Design Notes

In Berger (1985), the loss of an action is deterministic for a specific state of nature. This makes it hard to accommodate for aleatoric uncertainty.
One could, as perhaps suggested by the investment example in Chapter 1 of that book, include the outcome of all relevant unobserved variables in the state of nature, and thus include the aleatoric uncertainty in the epistemic uncertainty about the state of nature.
However, this solution seems unintuitive, loses the differentiation between the two kinds of uncertainty, and it also poses additional challenges in the context of inference.
The observational distribution depends on the state of nature, e.g., through true parameters that are contained in it.
For inference to be meaningful it is necessary that the same parameters govern the loss. However, if the outcome of all unobserved variables is already determined in the state of nature, these parameters cannot have an effect anymore.

