# -*- coding: utf-8 -*-
'''ARFFDocument (class)
'''

class ARFFDocument:
    '''
    Helper class for the creation of ARFF documents
    '''

    def __init__(self, relation, attributes={}, attribute_order=[], data=[]):
        '''
        Constructor of ARFFDocument

        Keyword arguments:
            relation (str): name of the document's relation
            attributes (dict): attributes as attribute_name, attribute_value pair (e.g. {'feature-0':'numeric', 'feature-1':['val1', 'val2']})
            attribute_order (list): the order of these attributes
            data (list): data in the document
        '''
        self.relation = relation
        self.attributes = attributes
        if len(attribute_order) < 1: # if no order is specified, just use the unordered dict keys
            attribute_order = attributes.keys()
        self.attribute_order = attribute_order
        self.data = []

    def add_attribute(self, key, values):
        '''
        Add an attribute to the document

        Keyword arguments:
            key (str): name of the attribute
            values (str, set, list): values which the attribute can assume
        '''
        if key not in self.attributes:
            self.attributes[key] = value

    def get_attribute(self, key):
        '''
        Returns an attribute's values

        Keyword arguments:
            key (str): name of the attribute

        Returns:
            str, set, list: values which the attribute can assume
        '''
        return self.attributes[key]

    def add_data(self, data_attributes):
        '''
        Add data to the document

        Keyword arguments:
            data_attributes (dict): data point and the attribute values
        '''
        self.data.append(data_attributes)

    def generate_document(self, filename):
        '''
        Generates the ARFF document and write it to file

        Keyword arguments:
            filename (str): path to where the ARFF file should be created
        '''
        with open(filename, 'w', encoding='utf8') as fop:
            fop.write('@RELATION ' + self.relation + '\n\n') # relation in header
            # define attributes
            for attribute_key in self.attribute_order:
                attribute_values = self.attributes[attribute_key]
                fop.write('@ATTRIBUTE ' + attribute_key + ' ')
                if type(attribute_values) in [set, list]: # can attribute assume multiple values?
                    attribute_values_str = '{'
                    for attribute_value in attribute_values:
                        attribute_values_str += str(attribute_value) + ','
                    attribute_values_str = attribute_values_str[:-1] + '}'
                else:
                    attribute_values_str = str(attribute_values)
                fop.write(attribute_values_str + '\n')
            # define data
            fop.write('\n@DATA\n')
            for data_element in self.data:
                data_element_str = ''
                for attribute_key in self.attribute_order: # retain order
                    data_element_str += str(data_element[attribute_key]) + ','
                data_element_str = data_element_str[:-1]
                fop.write(data_element_str + '\n')
