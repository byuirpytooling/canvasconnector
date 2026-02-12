# %%
def add(a: float, b: float) -> float:
    """Add two numbers together.

    This function is documented in a way that mkdocstrings can
    automatically extract and render.

    Args:
      a: float The first number to add.
      b: float The second number to add.

    Returns:
      float The sum of ``a`` and ``b``.

    Examples:
        >>> add(2, 3)
        5
        >>> add(-1.5, 0.5)
        -1.0
    """
    return a + b
# %%
