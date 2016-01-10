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

import inspect
import typing


def map_type(criteria, value):
    if isinstance(criteria, typing.TypingMeta):
        return __map_typing(criteria, value)

    if isinstance(criteria, type):
        if not isinstance(value, criteria):
            raise TypeError(
                'Expected value {!r} to be of type {}'.format(
                    value, criteria
                )
            )

    elif isinstance(criteria, tuple):
        for entry in criteria:
            try:
                return map_type(entry, value)

            except TypeError:
                continue

        raise TypeError(
            ('Value {!r} does not comform to any of the ' +
            'following criteria:\n{}').format(
                value, '\n'.join(str(criteria) for criteria in criteria)
            )
        )

    elif callable(criteria):
        if not criteria(value):
            raise TypeError(
                'Value {!r} expected to comform to criteria {}'.format(
                    value, criteria
                )
            )

    elif criteria == None:
        if value is not None:
            raise TypeError(
                'Expected None as argument instead of {!r}'.format(value)
            )

    else:
        raise InvalidCriteria(criteria)

    return value


def __map_typing(criteria, value):
    if issubclass(criteria, typing.Callable):
        return __map_callable(criteria, value)

    if not issubclass(type(value), criteria):
        raise TypeError(
            'Expected value {!r} to be of type {}'.format(
                value, criteria
            )
        )

    return value


def __map_callable(criteria, value):
    # NOTE: We only validate arguments and the return value, but not
    # any keyword arguments, since it is not specifiable with
    # typing.Callable[]
    argspec = inspect.getfullargspec(value)

    if criteria.__args__ != Ellipsis:
        pos_arg_types = tuple(
            argspec.annotations.get(key, typing.Any)
            for key in argspec.args
        )

        if pos_arg_types != criteria.__args__:
            raise TypeError(
                ('Callable arguments expected to be {!r} ' +
                'instead of {!r}').format(criteria.__args__, pos_arg_types)
            )

    retval_type = argspec.annotations.get('return', typing.Any)
    if retval_type != criteria.__result__:
        raise TypeError(
            ('Callable return value expected to be {!r} ' +
            'instead of {!r}').format(criteria.__result__, retval_type)
        )

    return value


def is_valid(criteria):
    try:
        map_type(criteria, None)

    except InvalidCriteria:
        return False

    except TypeError:
        pass

    return True


class InvalidCriteria(Exception):
    '''
    Signifies that the validation criteria passed to map_type() is invalid.
    '''

    def __init__(self, criteria):
        super().__init__(
            'Value type criteria {!r} is invalid'.format(criteria)
        )


__all__ = ['is_valid', 'map_type', 'InvalidCriteria']
