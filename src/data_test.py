from data import load
import unittest

file_names = [
    "src/output_test/membros-ativos-contracheque-01-2020.csv",
    "src/output_test/membros-ativos-verbas-indenizatorias-01-2020.csv",
]


class TestData(unittest.TestCase):
    def test_validate_existence(self):
        STATUS_DATA_UNAVAILABLE = 4
        with self.assertRaises(SystemExit) as cm:
            dados = load(file_names, "2021", "01")
            dados.validate("./output")
        self.assertEqual(cm.exception.code, STATUS_DATA_UNAVAILABLE)


if __name__ == "__main__":
    unittest.main()
