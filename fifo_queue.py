class FifoQueue:
    def __init__(self):
        self.queue = []
        self.last_queue_size = 0
        self.push_count = 0

    def push(self, item):
        self.queue.append(item)
        self.push_count += 1

    def get_push_count(self):
        return self.push_count

    def pop(self):
        if not self.is_empty():
            return self.queue.pop(0)

    def head(self):
        if not self.is_empty():
            return self.queue[0]
        else:
            return None
    
    def is_empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)

    def reset_change_flag(self):
        self.last_queue_size = self.size()
    
    def has_changed(self):
        if self.size() != self.last_queue_size:
            self.last_queue_size = self.size()
            return True
        else:
            return False

# Gratuitous change to test git