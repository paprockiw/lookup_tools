import csv

class LookupBase(object):
    def __init__(self):
        self.key_fields = []
        self.mapped = {}

    def _comparable(self, other):
        '''Helper function for building comparision methods in this class. It 
        checks to see if the object that is to be compared to the base object 
        is an instance of the same class, and has an equal number of fields in 
        its keys for comparison.'''
        assert isinstance(other, self.__class__), \
                'Argument must be instance of %s.' % self.__class__
        assert len(self.key_fields) == len(other.key_fields), \
                'Other object must have same number of key_fields'

    def _assign_attr(self, name, d):
        '''Helper function for assigning new attribute to object.'''
        r = Result(d)
        setattr(self, name, r)

    def match(self, other, attr_name): 
        '''Takes another lookup object and an attribute name as input. Then it 
        takes each item stored in the 'mapped' attribute on this object and 
        checks to see if that item's key is present in the 'mapped' attribute 
        of the other object. If the key is present in the other object, the 
        record from the other object is added to '''
        self._comparable(other)
        d = {}
        for key in self.mapped:
            if key in other.mapped:
                d.update({key:other.mapped[key]})
        self._assign_attr(attr_name, d)

    def merge(self, other, attr_name, *merge_fields):
        '''Works like a merge, but takes an arbitrary number of args that are 
        the names of fields on the object being passed to this function. When 
        a match is found between this and the other object, the data in the 
        fields on the other object are merged into the matching rows on this 
        object. The results are stored on an attribute you specify, as with 
        the match method.'''
        self._comparable(other)
        d = {}
        for key in self.mapped:
            if key in other.mapped:
                # get values to map to merge data fields
                field_values = [other.mapped[key][field] for field in merge_fields] 
                # make dict to merge
                new_items = dict(zip(merge_fields, field_values))
                records = self.mapped[key].copy() 
                records.update(new_items)
                d.update({key:records})
        self._assign_attr(attr_name, d)

    def diff(self, other, attr_name):
        '''The opposite of the match method, this takes another lookup object 
        and and an attribute name. It goes through each item in this object, 
        and looks for each item's key in the other object. If there is no 
        match, the item on this object is saved to the results, which are 
        stored on the attribute specified as an argument. '''
        self._comparable(other)
        d = {}
        for key in self.mapped:
            if key not in other.mapped:
                d.update({key:self.mapped[key]})
        self._assign_attr(attr_name, d)

    def write(self, title):
        ''' Takes a title as input and writes the values stored in the 
        'mapped' attribute to a new csv file with the title specified as an 
        argument.'''
        fieldnames = self.key_fields
        with open(title, 'wb') as output:
            writer = csv.DictWriter(output, fieldnames)
            writer.writeheader()
            for row in self.mapped.values():
                writer.writerow(row)

class Result(LookupBase):
    '''Object for storing results of comparison methods such as match or diff. 
    This can be used for further comparisons since it inherits from the base 
    object. '''
    def __init__(self, d):
        self.mapped = d
        self.key_fields = d[d.keys()[0]].keys()

class LookupMap(LookupBase):
    '''Object used for taking a csv file, and mapping its contents based on 
    the column names from the csv file. Each row of the csv file is entered 
    into a dictionary that has a tuple of the data in the specified rows as a 
    key, and the row itself (as a dictionary) as the associated value. This is 
    used for comparing data between this and other similar objects. '''
    def __init__(self, filename, *args):
        #super(LookupMap, self)
        self.mapped = {}
        self.filename = filename
        self.key_fields = args
        self.loss = []
        self._get_contents()

    def _get_contents(self):
        '''Loads the contents of the file into the lookup map structure.'''
        with open(self.filename, 'rb') as input:
            reader = csv.DictReader(input)
            # handle empty fields as a tuple of fieldnames from csv object
            if len(self.key_fields) == 0:
                self.key_fields = tuple(reader.fieldnames)
            for record in reader:
                key = tuple([record[k] for k in self.key_fields])
                if key in self.mapped:
                    # Adds items already in dict to 'loss' attr, so that items
                   # in dict are not overwritten and repeat data are preserved
                    self.loss.append(record)
                else: self.mapped.update({key:record})

    @property
    def loss_count(self):
        return len(self.loss)

if __name__ == '__main__':
    a = LookupMap('test1.csv', 'animal', 'number')
    b = LookupMap('test2.csv', 'creature', 'num')

#    a.match(b, 'b_match')
#    for row in a.b_match.mapped:
#        print row, a.b_match.mapped[row]
#
#    a.b_match.write('bmatch.csv')

    a.merge(b, 'b_merge', 'chemical', 'num')

    a.b_merge.write('merge_test.csv')
