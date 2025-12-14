import pygame as pg
from src.interface.components.chat_overlay import ChatOverlay


class FakeOnline:
    def __init__(self):
        self.sent = []

    def send_chat(self, text: str) -> bool:
        self.sent.append(text)
        return True

    def get_recent_chat(self, limit: int = 50):
        return [
            {"id": 1, "from": 0, "text": "hello", "ts": 0},
            {"id": 2, "from": 1, "text": "world", "ts": 0}
        ]


def run_test():
    pg.init()
    om = FakeOnline()
    overlay = ChatOverlay(om)

    # simulate open and typing 'hi' then submit
    overlay.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_RETURN))
    overlay.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_h, unicode='h'))
    overlay.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_i, unicode='i'))
    overlay.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_RETURN))

    assert om.sent == ['hi']
    overlay.update(0)
    assert overlay._messages and len(overlay._messages) <= overlay.max_lines
    print('ChatOverlay tests passed')


if __name__ == '__main__':
    run_test()
