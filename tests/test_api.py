# -*- coding: utf-8 -*-

from docpack_confluence import api


def test():
    _ = api


if __name__ == "__main__":
    from docpack_confluence.tests import run_cov_test

    run_cov_test(
        __file__,
        "docpack_confluence.api",
        preview=False,
    )
