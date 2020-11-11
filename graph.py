from collections import defaultdict

class Graph:
   def __init__(self):
      self.adj_list = defaultdict(set) # adj_list[u] = {(v, w), ...}
      self.ts = []
   
   def __str__(self):
      ans = ""
      for u in self.adj_list:
         for adj in self.adj_list[u]:
            ans += f"T{u} -{adj[1]}-> T{adj[0]}\n"
      return ans[:-1]

   def add_edge(self, u: str, v: str, w: int):
      self.adj_list[u].add((v, w))

   def remove_edge(self, u: str, v: str, w: int):
      self.adj_list[u].discard((v, w))

   def is_cyclic(self):
      path = set()
      visited = set()

      def dfs(u):
         if u in visited:
            return False
         visited.add(u)
         path.add(u)
         for adj in self.adj_list.get(u, set()):
            v = adj[0]
            if v in path or dfs(v):
               return True
         path.remove(u)
         self.ts.append(u)
         return False

      return any(dfs(u) for u in self.adj_list)

   def topo_sort(self):
      self.ts = []
      if (self.is_cyclic()):
         raise Exception("O grafo não tem uma ordenação topológica.")
      return self.ts[::-1]


if __name__ == "__main__":
   g = Graph()
   g.add_edge('0', '1', 1)
   g.add_edge('1', '2', 1)
   g.add_edge('2', '3', 1)
   g.add_edge('3', '0', 1)
   print(g.is_cyclic())
   g.remove_edge('3', '0', 1)
   print(g.topo_sort())
