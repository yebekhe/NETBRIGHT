import sys
import TLS_bypass

TLS_bypass.ThreadedServer('',int(sys.argv[1]), str(sys.argv[2]), int(sys.argv[3])).listen()
