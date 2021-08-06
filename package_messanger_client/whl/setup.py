from setuptools import setup

setup(name="Client",
      py_modules=["formclient"],
      install_requires=["greenlet==1.1.0",
                        "PyQt5==5.15.4",
                        "PyQt5-Qt5==5.15.2",
                        "PyQt5-sip==12.9.0",
                        "SQLAlchemy==1.4.22"],
      packages=["src","src/log"],
      )
