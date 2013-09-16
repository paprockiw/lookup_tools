import csv

class LookupBase(object):
    def __init__(self):
        self.key_fields = []
        self.mapped = {}

    def _comparable(self, other):
        assert isinstance(other, self.__class__), \
                'Argument must be instance of %s.' % self.__class__
        assert len(self.key_fields) == len(other.key_fields), \
                'Other object must have same number of key_fields'

    def _assign_attr(self, name, d):
        r = Result(d)
        setattr(self, name, r)

    def match(self, other, attr_name): 
        self._comparable(other)
        d = {}
        for key in self.mapped:
            if key in other.mapped:
                d.update({key:other.mapped[key]})
        self._assign_attr(attr_name, d)

    def diff(self, other, attr_name):
        self._comparable(other)
        d = {}
        for key in self.mapped:
            if key not in other.mapped:
                d.update({key:self.mapped[key]})
        self._assign_attr(attr_name, d)

class Result(LookupBase):
    def __init__(self, d):
        self.mapped = d
        self.key_fields = d[d.keys()[0]].keys()

class LookupMap(LookupBase):
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


a = LookupMap('test1.csv', 'animal', 'number')
b = LookupMap('test2.csv', 'creature', 'num')

a.match(b, 'b_match')
print a.b_match.mapped