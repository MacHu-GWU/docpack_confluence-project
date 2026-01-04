# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from docpack_confluence.tests import run_cov_test

    run_cov_test(
        __file__,
        "docpack_confluence",
        is_folder=True,
        preview=False,
    )
