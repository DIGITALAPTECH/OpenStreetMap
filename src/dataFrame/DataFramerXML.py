import inspect
import os
from abc import ABC
from abc import abstractmethod
from termcolor import colored
import xml.etree.cElementTree as ET

PWD = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
ROOT = os.path.join(PWD, '..', '..')
RES = os.path.join(ROOT, 'res')


class ParserXML(ABC):
	'''
	This is an abstract class used to
	parse the XML file. This returns
	a iterator to the XML file pointer
	which is then used by any other derived
	classes. This is respnsible for basic
	validation of '<osm>' tag in the OSM
	XML file. This is very memory efficient
	and because of the 'cElementTree', parsing
	is quick too. This class handles all the low
	level data parsing and file handling operation
	on raw xml file. This should not be changed
	for unless one knows what and why to change.

	:inherits: ABC - Abstract Base Class
	:abstractmethod: export_dataset - Export the dataset with
					additional parsing and logic
	'''

	def __init__(self, osmFile, events=('start', 'end')):
		if osmFile.split('.')[-1].lower() != 'osm':
			raise ValueError('Error in OSM file')
		self.source = os.path.join(RES, osmFile)
		self._context = iter(ET.iterparse(self.source, events=events))
		self._check_root()

	@property
	def context(self):
		return self._context

	def _check_root(self):
		_, self.root = next(self._context)
		if self.root.tag.lower() != 'osm':
			raise ValueError('OpenStreetDataMap Error')

	def _get_element(self, tags):
		for event, elem in self.context:
			if event == 'end' and elem.tag in self.tags:
				yield elem
				self.root.clear()

	@abstractmethod
	def export_dataset(default_path):
		pass


class DataFramerXML(ParserXML):
	'''
	This inhetits the 'ParserXML' abstract base
	class and implements the 'export_dataset'
	abstractmethod. This sends the 'tags' to
	the base class and data related to those
	tags are only fetched. This is also responsible
	to validate if false tags are supplied or not
	before it moves to the base class to parse the
	low level data.
	'''

	def __init__(self, osmFile, tags, **kwargs):
		super(self.__class__, self).__init__(osmFile=osmFile)
		self.tags = tags
		self.export_files = kwargs.get('files')
		self.export = kwargs.get('export')
		self.tagValidation = kwargs.get('tagValidation', False)
		self.rootPath = kwargs.get('root', '.')
		self._validate()

	def _validate(self):
		if not self.export:
			pass
		elif self.export is None and self.export_files is not None or self.export is not None and self.export_files is None:
			raise ValueError('Export value and export_files doesn\'t match')

		if self.tagValidation:
			allTags = set()
			print('In Progress Tag Validation. This may take some time depending on the XML file size.....')
			for event, elem in self.context:
				allTags.add(elem.tag)

			for each in self.tags:
				if each not in allTags:
					raise ValueError('Given tags are not present in XML')

	def export_dataset(self, default_path=RES):
		if not os.path.exists(self.rootPath):
			raise IOError('The path doesn\'t exist.')
		for export_file, factor in self.export_files.items():
			if export_file.split('.')[-1] != 'osm':
				raise ValueError('Export files must OSM type')
			with open(os.path.join(default_path, export_file), 'wb') as output:
				output.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
				output.write(b'<osm>\n  ')
				for i, element in enumerate(self._get_element(self.tags)):
					if i % factor == 0:
						output.write(ET.tostring(element, encoding='utf-8'))
				output.write(b'</osm>')
				self._context = iter(ET.iterparse(self.source, events=('start', 'end')))
				print(colored("[PASSED✓]", "green", attrs=['bold']) + " Created {} successfully".format(export_file))


# def main():
# 	tags = ('node', 'way', 'relation')
# 	files = {'data10.osm': 10, 'data100.osm': 100, 'data1000.osm': 1000, 'data10000.osm': 10000}
# 	raw_data = os.path.join(RES, 'gurugram.osm')
# 	p = DataFramerXML(raw_data, tags=tags, files=files)
# 	p.export_dataset()


# if __name__ == '__main__':
# 	main()
