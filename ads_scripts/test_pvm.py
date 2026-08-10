# PVM - Keep alive and listen for response
import sys, os, time

os.environ['HPEESOF_DIR'] = '<ADS_INSTALL>'
os.environ['HOME'] = '<ADS_INSTALL>\\Keysight ADS 2020\\home'
os.environ['EESOFPVM_TMP'] = '<TEMP>'

sys.path.insert(0, '<ADS_INSTALL>/fem/2020.20/win32_64/bin')
sys.path.insert(0, '<ADS_INSTALL>/pvm3/lib/clm')

import eesofpvm

mytid = eesofpvm.mytid()
print("My tid:", hex(mytid))

# Find eesofg2p
tasks = eesofpvm.tasks()
g2p_tid = None
for t in tasks:
    name = str(t[4]) if len(t) > 4 else ""
    if 'eesofg2p' in name:
        g2p_tid = t[0]
        print("Found eesofg2p:", hex(g2p_tid), "name:", name)
        break

if not g2p_tid:
    print("eesofg2p not found!")
    print("Available tasks:", tasks)
    sys.exit(1)

# Set up task name (may fail if already set from previous run)
try:
    eesofpvm.setjointaskname("pvm_probe_%d" % mytid)
except:
    pass

# Send command and wait for reply
cmd = 'fputs(stderr, "PVM_TEST_HELLO_FROM_PYTHON\\n")'
print("Sending to", hex(g2p_tid), ":", cmd)

bufid = eesofpvm.initsend()
eesofpvm.pkstr(cmd)
eesofpvm.send(g2p_tid, 0)
print("Sent!")

# Wait for response (timed recv, 5 second timeout)
print("Waiting for response (5s)...")
try:
    bufid = eesofpvm.trecv(-1, -1, 5000000)
    if bufid >= 0:
        info = eesofpvm.bufinfo(bufid)
        size, msgId, tid = info
        print("RESPONSE from", hex(tid), "msgId:", msgId, "size:", size)
        data = eesofpvm.upkstr()
        print("Data:", data)
    else:
        print("trecv returned:", bufid)
except Exception as e:
    print("trecv error:", type(e).__name__, str(e)[:200])

print("Done. Check ADS Message List for PVM_TEST_HELLO.")
