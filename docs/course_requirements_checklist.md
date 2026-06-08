# Course Requirements Checklist

This checklist translates the assignment into concrete deliverables for the final project.

## A. Mechanism-based modeling

- [x] Start from a classical predator-prey model rather than pure data fitting.
- [x] Include prey growth, predation, predator growth, predator death, and environmental limitation.
- [x] Introduce fear explicitly as a mechanism affecting prey effective reproduction.
- [x] Include a no-fear baseline for comparison.

Current implementation:

- `M0`: no-fear baseline
- `M1`: instant fear
- `M2`: memory fear

## B. Parameter-effect analysis

- [x] Analyze how fear intensity changes long-term behavior.
- [x] Analyze how memory update rate changes long-term behavior.
- [x] Provide parameter scans rather than isolated runs.

Current implementation:

- one-parameter `k` scan
- two-parameter `k-alpha` scan
- representative-case extraction

## C. Stability / oscillation / collapse discussion

- [x] Distinguish stable coexistence from oscillatory coexistence.
- [x] Track extinction or near-extinction risk.
- [x] Compare with the no-fear model.

Current implementation:

- classification labels:
  `stable_coexistence`, `oscillatory_coexistence`, `predator_extinct`, `prey_extinct`, `low_density_risk`, `invalid`

## D. Theory component

- [x] Provide model assumptions and notation.
- [x] Derive equilibrium conditions for the main model.
- [x] Derive local stability conditions for the main model.
- [x] Connect theory with numerics.

Current implementation:

- positivity and boundedness discussion
- positive equilibrium calculation
- Jacobian formulas
- Routh-Hurwitz stability conditions
- theory boundary overlay on the `k-alpha` scan

## E. Reasonable use of literature

- [x] Use literature to motivate model choice and parameter scales.
- [x] Avoid claiming unsupported exact reproduction of complex papers.
- [x] Keep the main model at a tractable course-project scale.

Current implementation:

- Wang 2016 for main fear mechanism
- Liu 2021 for delay and parameter references
- Yang and Jin 2022 for memory motivation
- Zhao 2025 for broader extension context

## F. Breadth without losing focus

- [x] Add at least one meaningful extension or comparison.
- [x] Keep one central model as the main contribution.

Current implementation:

- main contribution: `M2` memory fear
- controlled extensions:
  tritrophic, delay, Leslie-Gower, discrete-time map

## G. Final report quality target

Still needs careful final writing:

- [ ] Clearly separate analytical conclusions from numerical observations.
- [ ] Keep `M2` as the core storyline.
- [ ] Present extensions as supporting evidence, not competing main stories.
- [ ] Use figures and tables to back every major claim.

## Bottom line

The current consolidated final version already satisfies the substantive course requirements. The remaining work is mainly in final presentation quality and scientific tightening, not in basic model completeness.
