# -*- coding: utf-8 -*-

from pathlib import Path

from docpack_confluence.pack import SpaceExportConfig, ExportSpec
from docpack_confluence.tests.client import client
from docpack_confluence.tests.data import space_id

dir_here = Path(__file__).absolute().parent
dir_out = dir_here / "tmp"

spec = ExportSpec(
    space_configs=[
        SpaceExportConfig(
            client=client,
            space_id=space_id,
            include=[
                # f04-L4
                "https://sanhehu.atlassian.net/wiki/spaces/DPPROJ1/folder/655589823?atlOrigin=eyJpIjoiZWQ5ZDc4MmI1NzA3NDc4MWE3Zjg0NWZmNTZhOWM0YzgiLCJwIjoiYyJ9/*",
            ],
            exclude=[
                "https://sanhehu.atlassian.net/wiki/spaces/DPPROJ1/pages/655491623/p07-L7/**",
            ],
        ),
        SpaceExportConfig(
            client=client,
            space_id=space_id,
            include=[
                "https://sanhehu.atlassian.net/wiki/spaces/DPPROJ1/pages/655589958/p69-L4/**",
            ],
            exclude=[
                # p74-L9
                "https://sanhehu.atlassian.net/wiki/spaces/DPPROJ1/folder/655458912?atlOrigin=eyJpIjoiNzNiNGU0MDYwNjk5NGZlMmJlNDllMWM5YmM1MzNmODYiLCJwIjoiYyJ9/*",
            ],
        ),
    ],
    dir_out=dir_out,
)
spec.export()
