# LoRA: Parameter-Efficient Fine-Tuning

## What is LoRA?

**LoRA** (*Low-Rank Adaptation*) is a parameter-efficient method for fine-tuning large models.

- Freezes the original model weights — no updates to `W`
- Trains only small **adapter matrices** `A` and `B`
- Makes fine-tuning **cheaper**, **faster**, and **less memory-intensive**

---

## Core Formula

### Full Fine-Tuning *(standard approach)*

Every weight in the model is updated directly during training:

```
y = W_new · x
```

Where `W_new` is the result of gradient updates applied to the *entire* weight matrix:

```
W_new = W + ΔW
```

> `ΔW` here is a **full-rank** matrix — the same shape as `W`. For large models this is extremely expensive in memory and compute.

---

### LoRA *(parameter-efficient alternative)*

Instead of updating `W` directly, **freeze** it and learn a small low-rank correction on the side.

During training, the LoRA layer computes:

```
y = Wx + (α / r) · BAx
```

> The same input `x` is passed through **both** paths simultaneously — the frozen base weights `W` and the trainable adapter `BA` — and their outputs are summed into `y`.

After training, the adapter is **merged** into the base weights:

```
W_merged = W + (α / r) · BA
```

Then inference simply uses:

```
y = W_merged · x
```

> The key difference: LoRA's `ΔW = (α / r) · BA` is **low-rank** — `B` and `A` are tiny matrices, so only a fraction of the parameters of a full `ΔW` are ever trained.

---

## Components Explained

| Symbol | Meaning |
|--------|---------|
| `x` | **Input vector** to the layer — activations from the previous layer (e.g. a token embedding or hidden state) |
| `y` | **Output activations** produced by the layer |
| `W` | Original **frozen** base weight matrix |
| `A`, `B` | **Trainable** LoRA adapter matrices |
| `r` | LoRA **rank** (hyperparameter) |
| `α` | LoRA **scaling factor** (hyperparameter) |
| `ΔW` | Effective weight update = `(α / r) · BA` |

---

## The Merge Operation — Step by Step

The merge `W_merged = W + (α / r) · BA` involves three operations:

1. **Matrix multiplication** → `B × A = ΔW`
2. **Scalar multiplication** → `(α / r) · ΔW`
3. **Matrix addition** → `W + ΔW`

> LoRA computes a small low-rank weight update via matrix multiplication, then *adds* it to the original base weight matrix.

---

## Rank `r` — Adapter Capacity

`r` is chosen **before training** and controls the size of the adapter matrices.

- **Higher `r`** → more trainable parameters → better adaptation potential, but more memory/compute
- **Lower `r`** → smaller adapter → faster and cheaper, but less expressive
- The ratio `α / r` keeps the update scale **stable** when changing rank

---

## Alpha `α` — Scaling Factor

`α` controls **how strongly** the adapter update influences the base model.

- `α` **↑ bigger** → stronger adapter effect
- `α` **↓ smaller** → weaker adapter effect

**Example:**

```
r = 8
α = 16
α / r = 2.0   ← LoRA update BA is scaled by ×2 before merging
```

**Illustrative example — same adapter, different α:**

Suppose training converged and the adapter learned this update:

```
BA = [[ 0.1,  0.2 ],
      [ 0.3,  0.4 ]]
```

With `r = 8`, changing α changes how much of that update gets baked in:

| α | α / r | ΔW = (α / r) · BA | Effect |
|---|-------|--------------------|--------|
| 4 | 0.5 | `[[ 0.05, 0.10 ], [ 0.15, 0.20 ]]` | Half-strength — conservative update |
| 8 | 1.0 | `[[ 0.10, 0.20 ], [ 0.30, 0.40 ]]` | Full-strength — adapter applied as-is |
| 16 | 2.0 | `[[ 0.20, 0.40 ], [ 0.60, 0.80 ]]` | Double-strength — aggressive update |

> The adapter matrices `A` and `B` are **identical** in all three cases — only `α` differs. A larger `α` amplifies the learned correction; a smaller `α` suppresses it. This lets you tune the adapter's influence *without retraining*.

---

## Summary

> LoRA learns a **low-rank correction** `ΔW = (α / r) · BA` and adds it to frozen base weights. Only `A` and `B` are trained — the rest of the model is untouched.
