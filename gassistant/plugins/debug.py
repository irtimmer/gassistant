# Copyright (C) 2019 Iwan Timmer
# SPDX-License-Identifier: Apache-2.0

class Debug:

    def process_event(self, event):
        print(event)

def getInstance(_):
    return Debug()
