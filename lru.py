class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.order = []

    def get(self, key):
        if key in self.cache:
            self.move_to_end(key)
            return self.cache[key]
        else:
            return -1

    def put(self, key, value):
        if key in self.cache:
            self.cache[key] = value
            self.move_to_end(key)
        elif len(self.cache) < self.capacity:
            self.cache[key] = value
            self.order.append(key)
        else:
            oldest_key = self.order.pop(0)
            del self.cache[oldest_key]
            self.cache[key] = value
            self.order.append(key)

    def move_to_end(self, key):
        if key in self.order:
            self.order.remove(key)
        self.order.append(key)