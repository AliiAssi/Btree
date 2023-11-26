import time


class BTreeNode(object):
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.c = []


class Btree(object):
    def __init__(self, t):
        self.root = BTreeNode(leaf=True)
        self.t = t

    def bsearch(self, x, k):
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i = i + 1
        if i < len(x.keys) and k == x.keys[i]:
            return x, i
        elif x.leaf:
            return None
        else:
            return self.bsearch(x.c[i], k)

    def bsplit_child(self, x, i):
        t = self.t
        y = x.c[i]
        z = BTreeNode(leaf=y.leaf)
        z.keys = y.keys[t:2 * t]
        interkeys = x.keys[0:i] + [y.keys[t - 1]] + x.keys[i:]
        x.keys = interkeys
        intercc = x.c[0:i + 1] + [z] + x.c[i + 1:]
        x.c = intercc
        y.keys = y.keys[0:(t - 1)]
        if not y.leaf:
            z.c = y.c[t:(2 * t + 1)]
            y.c = y.c[0:t]

    def insert(self, k):
        r = self.root
        if len(r.keys) == (2 * self.t) - 1:
            s = BTreeNode()
            self.root = s
            s.c.insert(0, r)  # s.c[ 0 ] =  r
            self.bsplit_child(s, 0)
            self.insert_nonfull(s, k)
        else:
            self.insert_nonfull(r, k)

    def insert_nonfull(self, x, k):
        i = len(x.keys) - 1
        if x.leaf:
            x.keys.append(0)
            while i >= 0 and k < x.keys[i]:
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = k
        else:
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if len(x.c[i].keys) == (2 * self.t) - 1:
                self.bsplit_child(x, i)
                if k > x.keys[i]:
                    i += 1
            self.insert_nonfull(x.c[i], k)

    def delete(self, k):
        r = self.root
        i = len(r.keys) - 1
        while i >= 0 and k < r.keys[i]:
            i -= 1
        if r.leaf:
            if i >= 0 and r.keys[i] == k:
                r.keys.pop(i)
            return
        else:
            if i >= 0 and r.keys[i] == k:
                if len(r.c[i].keys) >= self.t:
                    r.keys[i] = self.delete_predecessor(r.c[i])
                    return
                elif len(r.c[i + 1].keys) >= self.t:
                    r.keys[i] = self.delete_successor(r.c[i + 1])
                    return
                else:
                    self.delete_merge(r, i, i + 1)
                    if len(r.c) == 1:
                        self.root = r.c[0]
                        del r
                    self.delete(k)
            else:
                i += 1
                if len(r.c[i].keys) == self.t - 1:
                    if i == 0:
                        self.delete_sibling(r, 1, 0)
                    elif i == len(r.keys):
                        self.delete_sibling(r, len(r.c) - 2, len(r.c) - 1)
                    elif len(r.c[i - 1].keys) > self.t - 1:
                        self.delete_sibling(r, i - 1, i)
                    else:
                        self.delete_sibling(r, i + 1, i)
                if i >= len(r.c):
                    self.delete_internal(r.c[-1], k)
                else:
                    self.delete_internal(r.c[i], k)

    def delete_predecessor(self, x):
        if x.leaf:
            return x.keys.pop()
        elif len(x.c[-1].keys) == self.t - 1:
            self.delete_sibling(x, len(x.c) - 2, len(x.c) - 1)
        return self.delete_predecessor(x.c[-1])

    def delete_successor(self, x):
        if x.leaf:
            return x.keys.pop(0)
        elif len(x.c[0].keys) == self.t - 1:
            self.delete_sibling(x, 1, 0)
        return self.delete_successor(x.c[0])

    def delete_merge(self, x, i, j):
        x.c[i].keys = x.c[i].keys + [x.keys.pop(i)] + x.c[j].keys
        if not x.c[i].leaf:
            x.c[i].c = x.c[i].c + x.c[j].c
        del x.c[j]
        if len(x.c) == 1:
            self.root = x.c[0]
            del x

    def delete_sibling(self, x, i, j):
        if i < j:
            if len(x.c[i].keys) == self.t - 1:
                self.delete_merge(x, i, j)
            else:
                x.c[j].keys = [x.keys[j]] + x.c[j].keys
                if not x.c[len(x.c) - 2].leaf:
                    x.c[j].c = [x.c[i].c.pop()] + x.c[j].c
                x.keys[j] = x.c[i].keys.pop()
        elif i > j:
            if len(x.c[i].keys) == self.t - 1:
                self.delete_merge(x, j, i)
            else:
                x.c[j].keys = x.c[j].keys + [x.keys[j]]
                if not x.c[i].leaf:
                    x.c[j].c = x.c[j].c + [x.c[i].c.pop(0)]
                x.keys[j] = x.c[i].keys.pop(0)

    def delete_internal(self, x, k):
        i = len(x.keys) - 1
        while i >= 0 and k < x.keys[i]:
            i -= 1
        if x.leaf:
            if i >= 0 and x.keys[i] == k and len(x.keys) > self.t - 1:
                x.keys.pop(i)
            return
        else:
            if i >= 0 and x.keys[i] == k:
                if len(x.c[i].keys) >= self.t:
                    x.keys[i] = self.delete_predecessor(x.c[i])
                    return
                elif len(x.c[i + 1].keys) >= self.t:
                    x.keys[i] = self.delete_successor(x.c[i + 1])
                    return
                else:
                    self.delete_merge(x, i, i + 1)
                    self.delete_internal(x, k)
            else:
                i += 1
                if len(x.c[i].keys) == self.t - 1:
                    if i == 0:
                        self.delete_sibling(x, 1, 0)
                    elif i == len(x.keys):
                        self.delete_sibling(x, len(x.c) - 2, len(x.c) - 1)
                    elif len(x.c[i - 1].keys) > self.t - 1:
                        self.delete_sibling(x, i - 1, i)
                    else:
                        self.delete_sibling(x, i + 1, i)
                if i >= len(x.c):
                    self.delete_internal(x.c[-1], k)
                else:
                    self.delete_internal(x.c[i], k)

    def print_levels(self, x, level=0):
        print("level=", level, " and keys root=", x.keys)
        level += 1
        for c in x.c:
            self.print_levels(c, level)

    def printing(self):
        self.print_levels(self.root)


if __name__ == "__main__":
    btree = Btree(t=2)

    for num in range(0, 10):
        btree.insert(num)

    btree.print_levels(btree.root)
    print(" after deletion")
    for num in range(9, -1, -1):
        print("the ", num, " deletion:")
        btree.delete(num)
        btree.printing()
        time.sleep(1)

