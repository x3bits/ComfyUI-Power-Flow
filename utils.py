def MakeSmartType(t):
    if isinstance(t, str):
        return SmartType(t)
    return t


class SmartType(str):
    def __ne__(self, other):
        if self == "*" or other == "*":
            return False
        selfset = set(self.split(','))
        otherset = set(other.split(','))
        return not selfset.issubset(otherset)


class DefaultValueWhenOutofRangeTuple(tuple):

    def __new__(cls, wrapped_tuple, default_value):
        instance = super().__new__(cls, wrapped_tuple)
        instance.default_value = default_value
        return instance

    def __getitem__(self, index):
        if isinstance(index, int):
            if -len(self) <= index < len(self):
                return super().__getitem__(index)
            return self.default_value
        elif isinstance(index, slice):
            return DefaultValueWhenOutofRangeTuple(
                super().__getitem__(index), self.default_value
            )
        else:
            raise TypeError("Index must be an integer or a slice.")


class DefaultValueWhenKeyMatchedDict(dict):
    def __init__(self, wrapped_dict, default_value, key_matcher):
        super().__init__(wrapped_dict)
        self.default_value = default_value
        self.key_matcher = key_matcher

    def __getitem__(self, key):
        if self.key_matcher(key):
            return self.get(key, self.default_value)
        return super().__getitem__(key)

    def __contains__(self, key):
        if self.key_matcher(key):
            return True
        return super().__contains__(key)
