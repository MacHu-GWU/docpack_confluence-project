# -*- coding: utf-8 -*-

from docpack_confluence.shortcuts import (
    get_space_by_id,
    get_space_by_key,
)


if __name__ == "__main__":
    from docpack_confluence.tests import run_cov_test

    run_cov_test(
        __file__,
        "docpack_confluence.shortcuts",
        preview=False,
    )
