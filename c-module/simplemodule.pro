TEMPLATE = lib
CONFIG += console
CONFIG -= app_bundle
CONFIG -= qt

SOURCES += \
    simplemodule.c

HEADERS +=


INCLUDEPATH += /usr/include/python3.8
LIBS += -L/usr/lib64/python3.8 -lpython3.8

DISTFILES += \
    setup.py
