from typing import Any, Dict, Optional, Sequence, Tuple, Union

Node = Any

def const(x: Any) -> Any: ...

#   0: return x
# ? 0: return x
def native(x: Any) -> Any: ...

#   0: return x
# ? 0: return x
def viper(x: Any) -> Any: ...

#   0: return x
# ? 0: return x
def mem_free() -> number: ...
def mem_alloc() -> number: ...
