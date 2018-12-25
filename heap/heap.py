"""This module implements the MinHeap and MaxHeap data structures.
For more information about the heap structure:
https://en.wikipedia.org/wiki/Heap_(data_structure)
"""
from math import ceil

class IndexOutOfRangeError(BaseException):
	pass

class InvalidElement(BaseException):
	pass

class EmptyHeapError(BaseException):
	pass

def _swap(array, index1, index2):
	temp = array[index1]
	array[index1] = array[index2]
	array[index2] = temp

class _Heap:
	def __init__(self):
		"""Initializes an empty heap of size 0."""
		self.size = 0
		self.heap_array = list()

	def __len__(self):
		return self.size

	def get_top(self):
		"""Returns the top element of the heap
		without removing it."""
		return self.heap_array[0]

	def insert(self, element):
		"""Inserts an element to the heap and puts it in
		it's appropriate position. The element cannot be None"""
		if element is None:
			raise InvalidElement
		self.heap_array.append(element)
		self.size += 1
		self._heapify_up(self.size - 1)

	def remove(self):
		"""Removes and returns the top element of the heap.
		If the heap is of size 0 raises EmptyHeapError."""
		if self.size == 0:
			raise EmptyHeapError
		_swap(self.heap_array, 0, self.size - 1)
		ret = self.heap_array.pop()
		self.size -= 1
		self._heapify_down(0)
		return ret

	def remove_gen(self):
		"""A generator that removes and returns the top element of
		the heap until it is empty."""
		while self.size:
			yield self.remove()

	@classmethod
	def from_iterable(cls, iterable):
		"""Builds a heap from an iterable. Returns the newly created
		heap."""
		heap = cls()
		for element in iterable:
			heap.insert(element)
		return heap

	def _parent(self, index, raise_exception = True):
		if index >= self.size:
			if raise_exception:
				raise IndexOutOfRangeError("Can't give the parent's index for element not in heap")
			else:
				return None
		return ceil(index / 2) - 1

	def _children(self, index, raise_exception = True):
		left = index * 2 + 1
		if left >= self.size:
			if raise_exception:
				raise IndexOutOfRangeError("Node at index {} does not have children".format(index))
			else:
				return (None, None)
		right = left + 1
		if left >= self.size:
			right = None
		return (left, right)

	def _compare(self, index1, index2, raise_exception = True):
		if max(index1, index2) >= self.size:
			if raise_exception:
				raise IndexOutOfRangeError()
		return self._compare_help(self.heap_array[index1], self.heap_array[index2])

	def _heapify_up(self, index):
		if index == 0:
			return
		parent = self._parent(index)
		if self._compare(index, parent): # swap
			_swap(self.heap_array, parent, index)
			self._heapify_up(parent)

	def _heapify_down(self, index):
		left, right = self._children(index, raise_exception = False)
		if left is None:
			return
		if right is None or right >= self.size:
			compare_index = left
		else:
			compare_index = left if self._compare(left, right) else right
		if self._compare(compare_index, index):
			_swap(self.heap_array, index, compare_index)
			self._heapify_down(compare_index)
	
	def _compare_help(self, element1, element2):
		raise NotImplementedError("Use MinHeap or MaxHeap")


class MinHeap(_Heap):
	"""A Minimum Heap priority queue. In this structure the smallest
	element is always at the top, and can be obtained by the remove method."""
	def _compare_help(self, element1, element2):
		if element1 < element2:
			return True
		return False

class MaxHeap(_Heap):
	"""A Maximum Heap priority queue. In this structure the largest
	element is always at the top, and can be obtained by the remove method."""
	def _compare_help(self, element1, element2):
		if element1 > element2:
			return True
		return False
