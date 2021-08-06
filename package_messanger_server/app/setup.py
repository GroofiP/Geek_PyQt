from setuptools import setup

setup(name="Server",
      py_modules=["formserver", "service", "servercls", "storagesqlite"],
      install_requires=["pyqt5==5.15.4"],
      packages=["src_log"],
      )
