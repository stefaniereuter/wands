"""
import the object logger from this file and log to it.

It writes all information to a log file, INFO to stdout, and warnings,
errors, to stderr.
"""
import sys
import os
import logging
from pathlib import Path
import re

# Allow set the directory to write the log files in with the environment
# variable WANDSLOGPATH
# Default to CWD
if LOGPATH:=os.environ.get("WANDSLOGPATH"):
    LOGPATH = Path(LOGPATH)
else:
    LOGPATH = Path(".")

LOGFILE = "WANDS"
n = 0
EXT = ".log"

pattern = LOGFILE + "(\d*)" + EXT

# Increment the n value
for f in os.listdir(LOGPATH):
    if res:=re.search(pattern, f):
        if int(res.group(1)) > n:
            n = int(res.group(1))

logging.basicConfig(filename=str(LOGPATH/(LOGFILE+n+EXT)),
                    level=logging.DEBUG)

logger = logging.getLogger("WANDS")

# Filter to isolate INFO for stdout
class _LoggingFilter(logging.Filter):
    def __init__(self, level: int):
        super().__init__()
        self._level = level
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self._level

# INFO to stdout
outhandler = logging.StreamHandler(sys.stdout)
outhandler.setLevel(logging.INFO)
outhandler.addFilter(_LoggingFilter(logging.INFO))

# WARNING and above to stderr
errhandler = logging.StreamHandler(sys.stderr)
errhandler.setLevel(logging.WARNING)

logger.addHandler(outhandler)
logger.addHandler(errhandler)
