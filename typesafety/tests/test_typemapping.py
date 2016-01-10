#
# Copyright (c) 2013-2015 BalaBit
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

import unittest
import typing

from .. import typemapping


class TestTypeMapping(unittest.TestCase):
    def test_map_scalar_type(self):
        self.assertEqual(1, typemapping.map_type(int, 1))
        self.assertEqual('a', typemapping.map_type(str, 'a'))
        self.assertEqual(object, typemapping.map_type(type, object))
        self.assertRaises(TypeError, typemapping.map_type, int, 'str')

    def test_oldschool_union_type(self):
        self.assertEqual(1, typemapping.map_type((int, str), 1))
        self.assertEqual('', typemapping.map_type((int, str), ''))
        self.assertRaises(
            TypeError,
            typemapping.map_type, (int, str), object()
        )

    def test_callable_validation_type(self):
        def argcheck(value):
            return value > 0

        self.assertEqual(1, typemapping.map_type(argcheck, 1))
        self.assertEqual('', typemapping.map_type((str, argcheck), ''))
        self.assertRaises(
            TypeError,
            typemapping.map_type, argcheck, -1
        )

    def test_invalid_criteria(self):
        self.assertRaises(
            typemapping.InvalidCriteria,
            typemapping.map_type, object(), 'anything'
        )

    def test_none_criteria(self):
        self.assertEqual(None, typemapping.map_type(None, None))
        self.assertRaises(
            TypeError,
            typemapping.map_type, None, 1
        )

    def test_typing_criteria(self):
        self.assertEqual(1, typemapping.map_type(typing.Optional[int], 1))
        self.assertEqual(
            None,
            typemapping.map_type(typing.Optional[int], None)
        )
        self.assertRaises(
            TypeError,
            typemapping.map_type, typing.Optional[int], object()
        )

    def test_map_callable(self):
        def example(x: int, y: str) -> str:
            return ''

        self.assertEqual(
            example,
            typemapping.map_type(typing.Callable[[int, str], str], example)
        )
        self.assertRaises(
            TypeError,
            typemapping.map_type, typing.Callable[[int, int], str], example
        )
        self.assertRaises(
            TypeError,
            typemapping.map_type, typing.Callable[[int, str], int], example
        )

    def test_missing_annotation_means_typing_any(self):
        def example(x: int, y: str):
            return ''

        self.assertEqual(
            example,
            typemapping.map_type(
                typing.Callable[[int, str], typing.Any],
                example
            )
        )
        self.assertRaises(
            TypeError,
            typemapping.map_type, typing.Callable[[int, str], str], example
        )

    def test_ellipse_means_no_args_check(self):
        def example(x: int, y: str) -> int:
            return ''

        self.assertEqual(
            example,
            typemapping.map_type(
                typing.Callable[..., int],
                example
            )
        )
        self.assertRaises(
            TypeError,
            typemapping.map_type, typing.Callable[..., str], example
        )

    def test_is_valid_criteria(self):
        self.assertTrue(typemapping.is_valid(None))
        self.assertTrue(typemapping.is_valid(int))
        self.assertTrue(typemapping.is_valid((int, str)))
        self.assertTrue(typemapping.is_valid(lambda v: True))
        self.assertTrue(typemapping.is_valid(typing.Union[int, str]))
        self.assertFalse(typemapping.is_valid(object()))
        self.assertFalse(typemapping.is_valid((int, object())))
