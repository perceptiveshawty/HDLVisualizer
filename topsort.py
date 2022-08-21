from collections import defaultdict

class Chip_Graph:
    def __init__(self, vertices):
        self.graph = defaultdict(list)
        self.V = vertices

    def add_edge(self, u, v):
        self.graph[u].append(v)

    def topological_sort_dfs(self, v, visited, chips):

        visited[v] = True
        for i in self.graph[v]:
            # print(i)
            if not visited[i]:
                self.topological_sort_dfs(i, visited, chips)
        chips.insert(0, v)

    def topological_sort(self):
        visited = []
        for i in range(self.V):
            visited.append(False)
        chips = []

        for i in range(self.V):
            if not visited[i]:
                self.topological_sort_dfs(i, visited, chips)

        return chips

class Chip_Graph_BFS:
    def __init__(self, vertices):
        self.graph = defaultdict(list) # dictionary containing adjacency List
        self.V = vertices # No. of vertices

    # function to add an edge to graph
    def add_edge(self, u, v):
        self.graph[u].append(v)


    # The function to do Topological Sort.
    def topological_sort(self):

        in_degree = [0]*(self.V)

        for i in self.graph:
            for j in self.graph[i]:
                in_degree[j] += 1

        queue = []
        for i in range(self.V):
            if in_degree[i] == 0:
                queue.append(i)

        cnt = 0

        top_order = []

        while queue:
            u = queue.pop(0)
            top_order.append(u)

            for i in self.graph[u]:
                in_degree[i] -= 1
                if in_degree[i] == 0:
                    queue.append(i)

            cnt += 1

        return top_order
