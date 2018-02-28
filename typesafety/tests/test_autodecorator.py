#
# Copyright (c) 2013-2018 BalaBit
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import sys
import unittest

from ..autodecorator import decorate_module


def mock_decorator(func):
    if not hasattr(func, '__name__'):
        return func

    if func.__name__ == '__init__':
        return func

    def __wrapper(*args, **kwargs):
        return 1234

    return __wrapper


class TestAutodecorate(unittest.TestCase):
    def setUp(self):
        from . import mockmodule
        self._module = mockmodule
        decorate_module(self._module, decorator=mock_decorator)

    def tearDown(self):
        self.__unload_test_module('mockmodule')
        self.__unload_test_module('mockmodule2')

    def test_module_function(self):
        self.assertEqual(1234, self._module.function())

    def test_object_method(self):
        self.assertEqual(1234, self._module.ModuleClass().method())

    def test_object_property(self):
        self.assertEqual(1234, self._module.ModuleClass().value)

    def test_object_classmethod(self):
        self.assertEqual(1234, self._module.ModuleClass.clsmethod())

    def test_object_staticmethod(self):
        self.assertEqual(1234, self._module.ModuleClass.staticmethod())

    def __unload_test_module(self, name):
        fullname = 'typesafety.tests.' + name

        if fullname in sys.modules:
            del sys.modules[fullname]

    def test_dont_decorate_objects_not_native_to_the_module(self):
        self.assertEqual(2, self._module.UndecoratedClass().method(1))
        self.assertEqual(3, self._module.undecorated_function(1))
