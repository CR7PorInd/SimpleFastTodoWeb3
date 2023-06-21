class Status(list):
    def __init__(self):
        super().__init__(['Not Completed', 'Completed', 'In Progress'])
        self.current = self[0]

    def as_list(self):
        return sorted(self)

    def print(self):
        print(self)

    def set_current(self, status: str):
        if status in self:
            self.current = status


if __name__ == '__main__':
    pass
