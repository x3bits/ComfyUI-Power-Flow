import unittest
import json
from hack import DefaultValueWhenKeyMatchedDict, DefaultValueWhenOutofRangeTuple

class TestDefaultValueWhenKeyMatchedDict(unittest.TestCase):
    def setUp(self):
        self.wrapped_dict = DefaultValueWhenKeyMatchedDict(
            {'a': 1, 'b': 2}, 
            'default', 
            lambda k: isinstance(k, str) and k.startswith('initial_value_')
        )

    def test_basic_operations(self):
        # 测试基本获取操作
        self.assertEqual(self.wrapped_dict['a'], 1)
        self.assertEqual(self.wrapped_dict['b'], 2)
        self.assertEqual(self.wrapped_dict['initial_value_1'], 'default')
        self.assertEqual(self.wrapped_dict['initial_value_2'], 'default')
        
        # 测试不存在的键
        with self.assertRaises(KeyError):
            self.wrapped_dict['c']

    def test_modification(self):
        # 测试修改和添加
        self.wrapped_dict['a'] = 10
        self.wrapped_dict['c'] = 3
        self.assertEqual(self.wrapped_dict['a'], 10)
        self.assertEqual(self.wrapped_dict['c'], 3)

        # 测试删除
        del self.wrapped_dict['b']
        self.assertNotIn('b', self.wrapped_dict)

    def test_dict_methods(self):
        # 测试字典方法
        self.assertEqual(len(self.wrapped_dict), 2)
        self.assertEqual(set(self.wrapped_dict.keys()), {'a', 'b'})
        self.assertEqual(set(self.wrapped_dict.values()), {1, 2})
        self.assertEqual(set(self.wrapped_dict.items()), {('a', 1), ('b', 2)})

    def test_update(self):
        # 测试更新方法
        self.wrapped_dict.update({'d': 4, 'e': 5})
        self.assertEqual(self.wrapped_dict['d'], 4)
        self.assertEqual(self.wrapped_dict['e'], 5)

    def test_json_serialization(self):
        # 测试JSON序列化
        self.assertEqual(json.dumps(self.wrapped_dict), '{"a": 1, "b": 2}')
        # 测试带有默认值的序列化
        self.wrapped_dict['initial_value_1'] = 'test'
        self.assertEqual(json.dumps(self.wrapped_dict), '{"a": 1, "b": 2, "initial_value_1": "test"}')

class TestDefaultValueWhenOutofRangeTuple(unittest.TestCase):
    def setUp(self):
        self.wrapped_tuple = DefaultValueWhenOutofRangeTuple((1, 2, 3), 'hello')

    def test_json_serialization(self):
        # 测试基本JSON序列化
        self.assertEqual(json.dumps(self.wrapped_tuple), '[1, 2, 3]')
        # 测试空元组序列化
        empty_tuple = DefaultValueWhenOutofRangeTuple((), 'default')
        self.assertEqual(json.dumps(empty_tuple), '[]')

    def test_basic_operations(self):
        # 测试基本操作
        self.assertEqual(len(self.wrapped_tuple), 3)
        self.assertEqual(list(self.wrapped_tuple), [1, 2, 3])
        self.assertIn(2, self.wrapped_tuple)
        self.assertNotIn(4, self.wrapped_tuple)

    def test_indexing(self):
        # 测试索引访问
        self.assertEqual(self.wrapped_tuple[0], 1)
        self.assertEqual(self.wrapped_tuple[2], 3)
        self.assertEqual(self.wrapped_tuple[5], 'hello')
        self.assertEqual(self.wrapped_tuple[-1], 3)
        self.assertEqual(self.wrapped_tuple[-5], 'hello')

    def test_slicing(self):
        # 测试切片操作
        sliced = self.wrapped_tuple[1:3]
        self.assertEqual(list(sliced), [2, 3])
        self.assertEqual(sliced[10], 'hello')

if __name__ == '__main__':
    unittest.main() 