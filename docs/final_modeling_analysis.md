# Final Modeling Analysis

## 1. Project objective

The assignment asks for mechanism-based modeling of predator-prey dynamics under fear effects, rather than data-driven forecasting. The strongest final version therefore needs:

- a clear baseline model for comparison
- one main innovation that is mathematically interpretable
- theory and numerics that speak to each other
- enough extensions to show breadth without weakening the main line

The consolidated final project uses memory-mediated fear as the main contribution and treats delay, tritrophic, Leslie-Gower, and discrete models as controlled extensions.

## 2. Final model hierarchy

### M0: no-fear baseline

```text
x' = r x - d1 x - d2 x^2 - p x y / (1 + h x)
y' = eta p x y / (1 + h x) - d3 y
```

Role:

- provides the comparison baseline
- identifies whether oscillation already exists without fear
- gives a clean starting point for equilibrium and stability analysis

### M1: instant fear

```text
x' = r x / (1 + k y) - d1 x - d2 x^2 - p x y / (1 + h x)
y' = eta p x y / (1 + h x) - d3 y
```

Role:

- captures non-consumptive fear in the simplest way
- keeps fear attached only to effective prey reproduction
- allows clean comparison with Wang et al. (2016)

### M2: memory fear

```text
x' = r x / (1 + k z) - d1 x - d2 x^2 - p x y / (1 + h x)
y' = eta p x y / (1 + h x) - d3 y
z' = alpha (y - z)
```

Role:

- this is the main model of the project
- `z(t)` is a smoothed risk perception variable, not a third species
- `alpha` controls memory length:
  larger `alpha` means shorter memory, smaller `alpha` means longer memory

Why this is the best main model:

- it stays interpretable
- it adds one state variable without making the system opaque
- it supports both mathematical stability work and rich numerical phase behavior

### M3: tritrophic extension

```text
X' = r X / (1 + k1 Y) - dX X - aX X^2 - p1 X Y / (1 + h1 X)
Y' = eta1 p1 X Y / (1 + h1 X) / (1 + k2 Z) - dY Y - p2 Y Z / (1 + h2 Y)
Z' = eta2 p2 Y Z / (1 + h2 Y) - dZ Z
```

Role:

- demonstrates that fear feedback is not limited to one trophic level
- broadens the ecological interpretation
- should remain an extension, not the main theorem-bearing model

## 3. Theory line that should anchor the final paper

The strongest final paper should anchor theory around M2.

### 3.1 Positivity

For positive initial data, the nonnegative region is invariant.

Reason:

- prey and predator equations are multiplicative in `x` and `y`
- the memory equation satisfies `z' = alpha (y - z)`, so when `z = 0` and `y > 0`, then `z' > 0`

### 3.2 Boundedness

The prey equation satisfies

```text
x' <= (r - d1) x - d2 x^2
```

which gives an upper logistic envelope. Once `x` is bounded, a weighted combination such as `W = eta x + y` controls predator growth. Since `z` exponentially relaxes toward `y`, boundedness of `y` implies boundedness of `z`.

### 3.3 Positive equilibrium

For M1 and M2, the positive equilibrium satisfies `z* = y*` and

```text
x* = d3 / (eta p - d3 h),   if eta p > d3 h
```

and `y*` comes from a scalar quadratic equation in `k`.

This is a major strength of the chosen model: memory changes stability, but not the equilibrium location.

### 3.4 Stability and Routh-Hurwitz

The M2 Jacobian can be written as

```text
J = [[A, B, C],
     [D, 0, 0],
     [0, alpha, -alpha]]
```

with characteristic polynomial

```text
lambda^3 + A1 lambda^2 + A2 lambda + A3 = 0
```

where

```text
A1 = alpha - A
A2 = -A alpha - B D
A3 = -alpha D (B + C)
```

and the local asymptotic stability condition is

```text
A1 > 0, A2 > 0, A3 > 0, A1 A2 > A3
```

This gives a clean theory boundary that can be overlaid on the numerical `k-alpha` classification map.

## 4. Numerical analysis strategy

The final project should present numerics in the following order.

### 4.1 Baseline comparisons

Compare:

- M0 no fear
- M1 instant fear
- M2 fast memory
- M2 slow memory

Purpose:

- show the modeling progression
- visually explain what memory changes

### 4.2 One-parameter `k` scan

Track tail means, amplitudes, and extrema as fear intensity changes.

Purpose:

- identify whether fear suppresses or preserves oscillations
- show how predator density changes with fear

### 4.3 Two-parameter `k-alpha` scan

Classify the long-term behavior into:

- stable coexistence
- oscillatory coexistence
- predator extinct
- prey extinct
- low-density risk
- invalid

Purpose:

- this is the main global numerical picture
- it shows how fear intensity and memory rate jointly structure the phase diagram

### 4.4 Theory overlay

Overlay the Routh-Hurwitz margin boundary on the numerical class map.

Purpose:

- connect theorem-level local stability with computed long-time behavior
- discuss where they agree and where finite-time or nonlinear effects create mismatch

### 4.5 Robustness across fear functions

Compare:

- rational form `1 / (1 + k z)`
- exponential form `exp(-k z)`
- quadratic rational form

Purpose:

- prevent the main conclusions from depending on a single algebraic choice

### 4.6 Representative cases

The strongest three cases are:

- Case A: no-fear oscillation becomes stable under stronger fear
- Case B: fear lowers predator peaks but oscillation remains under long memory
- Case C: long memory induces or amplifies oscillation while fast memory is stable

These cases turn the parameter scan into a narrative.

## 5. Role of the extension models

The extensions are useful, but they should be framed correctly.

### Delay extension

Interpretation:

- prey reacts to delayed predator risk rather than current risk

Value:

- strengthens the discussion around historical risk and lagged feedback
- connects directly to Liu et al. (2021)

Limit:

- do not let this replace the memory model as the central contribution

### Leslie-Gower comparison

Interpretation:

- alternative predator regulation and functional response structure

Value:

- shows that the project is not tied to a single baseline ecological mechanism

Limit:

- should be presented as structural comparison, not part of the main theorem chain

### Discrete-time map

Interpretation:

- generational update version of fear-mediated predator-prey interaction

Value:

- reveals discrete dynamics, bifurcation clouds, and possible stronger complexity

Limit:

- keep it explicitly separate from the continuous-time main model

## 6. What is already strong in the consolidated final version

- theory for M1 and M2 is explicit and code-backed
- the main numerical workflow is reproducible from one entry point
- the `k-alpha` scan is computationally structured rather than ad hoc
- robustness and representative-case logic are built in
- tritrophic, delay, Leslie-Gower, and discrete extensions are now in the same codebase
- literature notes are already organized into reusable writing assets

## 7. What should be emphasized in the final write-up

The final paper should not claim:

- precise prediction of a real ecological system
- empirical calibration beyond order-of-magnitude illustration
- full theory for all extensions

It should claim:

- a coherent mechanism-based modeling framework
- a rigorous theory-and-simulation study of how fear and memory alter stability
- a controlled comparison across several extensions that shows breadth without losing focus

## 8. Recommended writing structure

1. Background and ecological motivation
2. Literature review and modeling gap
3. Assumptions and notation
4. Model hierarchy M0-M3
5. Theory for M1-M2
6. Numerical methods and classification rules
7. Main results: baseline, `k` scan, `k-alpha` scan, theory overlay
8. Robustness and representative cases
9. Extensions: tritrophic, delay, Leslie-Gower, discrete
10. Discussion, limitations, and future work

## 9. Recommended main claim

The most defensible central claim is:

Fear does not simply reduce population size. Through the joint action of fear intensity and memory update rate, it can stabilize coexistence, preserve oscillations with reduced predator peaks, or create delayed-feedback risk regions that are not visible in a no-fear model.
