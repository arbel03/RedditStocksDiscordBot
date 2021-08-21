from ..util import is_test_mode

from sqlalchemy import Column, Boolean, DateTime, Enum, Float, ForeignKey
from sqlalchemy.orm import composite

if is_test_mode():
    from sqlalchemy import VARCHAR as VARCHAR
    from sqlalchemy import CLOB as CLOB
else:
    from sqlalchemy.dialects.oracle import CLOB as CLOB
    from sqlalchemy.dialects.oracle import VARCHAR2 as VARCHAR
    