import pathlib
import sys
import unittest

script_dir = pathlib.Path(__file__).resolve().parent


def main():
    loader = unittest.defaultTestLoader
    suite = loader.discover(str(script_dir))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print()
    # If there were any failures or errors, exit 1
    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    main()
