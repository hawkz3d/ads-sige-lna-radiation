import sys, os
os.environ['PATH'] = '<ADS_INSTALL>/bin;' + os.environ.get('PATH', '')

sys.path.insert(0, '<ADS_INSTALL>/circuit/win32_64/python/simInterface')
sys.path.insert(0, '<ADS_INSTALL>/circuit/win32_64/python/application')

print("Python version:", sys.version)

try:
    import ADSSim
    print("ADSSim OK:", dir(ADSSim))
except Exception as e:
    print("ADSSim error:", e)

try:
    import Design
    print("Design OK:", dir(Design))
except Exception as e:
    print("Design error:", e)

try:
    import Component
    print("Component OK:", dir(Component))
except Exception as e:
    print("Component error:", e)
