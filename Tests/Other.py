import random
import unittest

from TM1py.Objects import MDXView
from TM1py.Services import TM1Service
from TM1py.Utils import Utils

# Configuration for tests
address = 'localhost'
port = 8001
user = 'admin'
pwd = 'apple'
ssl = False
dimension_prefix = 'TM1py_unittest_dimension_{}'


class TestOtherMethods(unittest.TestCase):
    tm1 = TM1Service(address=address, port=port, user=user, password=pwd, ssl=ssl)

    def test1_execute_mdx(self):
        cube_names = self.tm1.cubes.get_all_names()
        cube_name = cube_names[random.randrange(0, len(cube_names))]
        _, public_views = self.tm1.views.get_all(cube_name=cube_name)
        # if no views on cube. Recursion
        if len(public_views) == 0:
            self.test1_execute_mdx()
        else:
            # random public view on random cube
            view = public_views[random.randrange(0, len(public_views))]
            # if random view is MDXView. Recursion
            if isinstance(view, MDXView):
                self.test1_execute_mdx()
            else:
                # if native view has no dimensions on the columns. Recursion
                if len(view._columns) == 0:
                    self.test1_execute_mdx()
                else:
                    # sum up all numeric cells in Native View
                    data_native_view = self.tm1.data.get_view_content(cube_name, view.name, private=False)
                    sum_native_view = sum(
                        [float(cell['Value']) for cell in data_native_view.values() if str(cell['Value']).isdigit()])

                    # get mdx from native view
                    mdx = view.as_MDX
                    # sum up all numeric cells in the response of the mdx query
                    data_mdx = self.tm1.data.execute_mdx(mdx)
                    sum_mdx = sum([float(cell['Value']) for cell in data_mdx.values() if str(cell['Value']).isdigit()])

                    # test it !
                    self.assertEqual(sum_mdx, sum_native_view)

    def test2_read_cube_name_from_mdx(self):
        all_cube_names = self.tm1.cubes.get_all_names()
        all_cube_names_normalized = [cube_name.upper().replace(" ", "") for cube_name in all_cube_names]
        for cube_name in all_cube_names:
            private_views, public_views = self.tm1.views.get_all(cube_name)
            for view in private_views + public_views:
                mdx = view.MDX
                cube_name = Utils.read_cube_name_from_mdx(mdx)
                self.assertIn(cube_name, all_cube_names_normalized)


if __name__ == '__main__':
    unittest.main()
