#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class StatusTracker:
    def __init__(self):
        self.past_states = []
        self.current_state = None

    def update_status(self, state, ref=None, source=None,
                      data=None, attempt=None):
        if self.current_state:
            self.past_states.append(self.current_state)
        self.current_state = state

    def update_result(self, step, status, percentage, message):
        pass
