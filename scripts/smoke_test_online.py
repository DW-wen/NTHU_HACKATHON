from src.core.managers.online_manager import OnlineManager
om = OnlineManager()
ok = om.update(10, 20, 'map.tmx', direction='left', moving=True)
print('update queued:', ok)
print('queue size (max 10):', om._update_queue.qsize())
# Peek latest
try:
    latest = om._update_queue.get_nowait()
    print('latest:', latest)
except Exception as e:
    print('error getting from queue', e)
