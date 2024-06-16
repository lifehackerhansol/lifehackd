#
# Copyright (C) 2024 lifehackerhansol
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#

import json
from typing import Any, Dict


def loadConfiguration() -> Dict[str, Any]:
    # Load config
    with open("config.json", "r") as f:
        config = json.load(f)

    botConfig = {}
    # bot internals
    botConfig['TOKEN'] = config['TOKEN']
    botConfig['PREFIX'] = [x for x in config['PREFIX']]

    return botConfig
