import json
import unittest

from . import jsonapi


class JsonAPITest(unittest.TestCase):

    def test_general(self):
        specification = jsonapi.Specification()
        specification.add_method(self.simple_method)

        json_str = '''{
            "method" : "simple_method",
            "args" : {
                "a" : 1,
                "b" : 2
            }
        }
        '''
        json_obj = json.loads(json_str)


    def simple_method(self, a: int, b: int) -> int:
        return a + b


if __name__ == '__main__':
    unittest.main()
