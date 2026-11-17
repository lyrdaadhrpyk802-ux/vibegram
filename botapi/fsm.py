# ============================================
#  botapi/fsm.py - Finite State Machine for Bots
#  All code and comments are English. No emojis.
# ============================================

class State:
    """Represents a specific state in a conversation."""
    def __init__(self, name=None):
        self.name = name or self.__class__.__name__
    
    def __str__(self):
        return self.name

class StatesGroup:
    """Base class for defining groups of states."""
    pass

class MemoryStorage:
    """In-memory storage for user states (resets on bot restart)."""
    def __init__(self):
        self._data = {}

    def set_state(self, user_id, state):
        self._data[user_id] = state

    def get_state(self, user_id):
        return self._data.get(user_id)

    def clear_state(self, user_id):
        self._data.pop(user_id, None)
