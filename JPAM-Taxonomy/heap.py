import heapq


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def enq(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def deq(self):
        return heapq.heappop(self.elements)

    def peek(self):
        return self.elements[0]
