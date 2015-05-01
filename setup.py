from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

base = 'Console'

executables = [
    Executable('pymaster.py', base=base)
]

setup(name = 'PyMaster',
      version = '0.7',
      description = 'Virtual master/mistress program.',
      options = dict(build_exe = buildOptions),
      executables = executables)
