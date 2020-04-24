#!/usr/bin/python3
from abc import ABCMeta as NativeABCMeta
from abc import abstractmethod, ABC

'''
Adapted from https://stackoverflow.com/a/50381071 with some edits of my own.
'''

class DummyAttribute:
	pass

def abstract_attribute(obj=None):
	if obj is None:
		obj = DummyAttribute()
	obj.__is_abstract_attribute__ = True
	return obj


class ABCMeta(NativeABCMeta):
	'''
	Check for abstract attributes in a way that's simpler to implement than the
	native strategy (https://stackoverflow.com/a/41897823) and also allows for
	abstract *instance attributes* set in __init__(), and not just abstract
	class attributes defined outside __init__().
	'''
	def __call__(cls, *args, **kwargs):
		instance = NativeABCMeta.__call__(cls, *args, **kwargs)
		abstract_attrs = ({name for name in dir(instance)
		                   if getattr(getattr(instance, name),
		                              '__is_abstract_attribute__', False)})

		if abstract_attrs:
			cls_name = cls.__name__
			attr_str = ', '.join(abstract_attrs)
			num_missing = len(abstract_attrs)
			raise NotImplementedError(f"Children of abstract class {cls_name} "
			                          f"must define {attr_str} as attribute "
			                          f"{'s' if num_missing > 1 else ''}")

		return instance

class ABC(metaclass=ABCMeta):
	'''
	(Copied directly from `abc`, though its metaclass is the new ABCMeta.)

	Helper class that provides a standard way to create an ABC using
	inheritance.
	'''
	__slots__ = ()
