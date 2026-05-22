# JSG Utils Node Context

This file stores durable implementation notes for general JSG utility nodes outside the Random Prompt Builder V2 subsystem.

## Always Load Convention

- General utility nodes that need to execute every queue run expose an `always_load` boolean input.
- Their `IS_CHANGED` method returns `float("NaN")` when `always_load` is enabled.
- When `always_load` is disabled, simple deterministic nodes may return a hash of their input kwargs.

## Value Stepper

- `nodes/JSGValueStepper.py` registers as `Value Stepper` under `JSG Utils/Number`.
- Inputs are `value` (`FLOAT`), `mode` (`increment` / `decrement`), `step` (`FLOAT`), `include_start` (`BOOLEAN`), and `always_load` (`BOOLEAN`).
- With `include_start=false`, outputs are the stepped value as nearest `INT`, 2-decimal rounded `FLOAT`, and 2-decimal formatted `STRING`.
- With `include_start=true`, outputs are the current starting value, while the widget is still updated to the stepped value for the next run.
- `js/JSGValueStepper.js` always moves the `value` widget to the stepped value after successful execution so the next manual run reuses it.
- Example with `include_start=false`: `value=1.1`, `mode=decrement`, `step=0.1` outputs `1`, `1.0`, and `1.00`, then sets the widget value to `1.0`.
- Example with `include_start=true`: `value=1.0`, `mode=decrement`, `step=0.1` outputs `1`, `1.0`, and `1.00`, then sets the widget value to `0.9`; the next run outputs `0.9`.
