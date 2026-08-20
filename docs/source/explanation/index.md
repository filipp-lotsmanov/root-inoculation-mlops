# Explanation

:::{note}
**Explanation** pages help you understand how the system works and
why it's built the way it is. They don't tell you how to do
anything — for that, see [How-to](../how-to/index).
:::

```{toctree}
:maxdepth: 1
:hidden:

architecture
security-model
error-codes
```

## What you'll find here

- {doc}`architecture` — the big picture: CLI, API, and Azure ML
  scoring share one inference path; why FastAPI, why U-Net, why
  patch-based inference; how the stack is containerised, deployed,
  and monitored.
- {doc}`security-model` — three credential types resolved to one
  identity, the three access tiers, constant-time API-key lookup,
  and the threat model.
- {doc}`error-codes` — how errors are reported, and why the
  `error_code` is separated from the `message`.
