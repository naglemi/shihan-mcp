
# Test file with creed violations

def check_value(value):
    # Violation: is None check
    if value is None:
        return 0
    
    # Violation: **kwargs
    def inner_func(**kwargs):
        return kwargs.get('x', 0)
    
    # Violation: mock
    from unittest.mock import MagicMock
    mock_obj = MagicMock()
    
    # Violation: hasattr
    if hasattr(value, 'compute'):
        return value.compute()
    
    return value
