import signal
import sys

if sys.platform == "win32":
    # Add all Unix signals that Windows doesn't have
    if not hasattr(signal, 'SIGHUP'):
        signal.SIGHUP = 1
    if not hasattr(signal, 'SIGQUIT'):
        signal.SIGQUIT = 3
    if not hasattr(signal, 'SIGTSTP'):
        signal.SIGTSTP = 18
    if not hasattr(signal, 'SIGCONT'):
        signal.SIGCONT = 19
    if not hasattr(signal, 'SIGTTIN'):
        signal.SIGTTIN = 21
    if not hasattr(signal, 'SIGTTOU'):
        signal.SIGTTOU = 22
    if not hasattr(signal, 'SIGWINCH'):
        signal.SIGWINCH = 28