import threading


def test():
    return 1


t = threading.Thread(target=test)
print(t.start())
