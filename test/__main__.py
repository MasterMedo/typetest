from unittest import defaultTestLoader, runner


def run():
    runner.TextTestRunner().run(defaultTestLoader.discover('.'))


if __name__ == '__main__':
    run()
