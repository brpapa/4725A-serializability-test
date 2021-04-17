from typing import List
from graph import Graph

def TO_test(schedule: List[str]):
   "Verifica se a escala é legal segundo o protocolo Timestamp Ordering."
   
   data_items = set(map(lambda instruction : instruction[2], schedule))
   transactions = list(dict.fromkeys(map(lambda instruction : instruction[0], schedule)))

   ts = dict() # TS(T): timestamp do início da transação T
   for i in range(len(transactions)):
      ts[transactions[i]] = i*10 + 10

   r_ts = dict() # R_timestamp(Q): timestamp da transação que leu Q pela última vez
   w_ts = dict() # W_timestamp(Q): timestamp da transação que escreveu Q pela última vez
   for data in data_items:
      r_ts[data] = w_ts[data] = 0

   for instruction in schedule:
      transaction, action, data = instruction

      if action == 'R':
         if ts[transaction] < w_ts[data]:
            # leitura rejeitada e transaction deve ser desfeita
            return f'Falha na transação {transaction} em {action}({data})'
         if ts[transaction] >= w_ts[data]:
            # leitura executada
            r_ts[data] = max(r_ts[data], ts[transaction])

      if action == 'W':
         if ts[transaction] < r_ts[data]:
            # escrita é rejeitada e transaction deve ser desfeita
            return f'Falha na transação {transaction} em {action}({data})'
         elif ts[transaction] < w_ts[data]:
            # escrita é rejeitada e transaction deve ser desfeita
            return f'Falha na transação {transaction} em {action}({data})'
         else:
            # escrita executada
            w_ts[data] = ts[transaction]

   return f'A escala é legal segundo o protocolo TO.\nR_timestamp: {r_ts}\nW_timestamp: {w_ts}'

def conflict_serializability_test(schedule: List[str]):
   "Verifica se a escala é serializável no conflito."

   g = Graph()

   for i in range(len(schedule)):
      current = schedule[i]
      others = [s for s in schedule[i+1:] if s[0] != current[0] and (s[1] != "R" or current[1] != "R") and s[2] == current[2]]

      # print(f"{current} {others}")
      for other in others:
         g.add_edge(current[0], other[0], 0)

   if g.is_cyclic():
      return f"Grafo de precedência:\n{g}\nA escala não é serializável no conflito, pois o grafo de precedência é cíclico."
   return f"Grafo de precedência:\n{g}\nA escala é serializável no conflito, pois o grafo de precedência não é cíclico"

def view_serializability_test(schedule: List[str]):
   "Verifica se a escala é serializável na visão."

   data_items = list(dict.fromkeys(map(lambda instruction: instruction[2], schedule)))
   begin = [f"bW{data}" for data in data_items]
   final = [f"fR{data}" for data in data_items]
   schedule = begin + schedule + final

   g = Graph()

   optional_edges = []
   for i in range(len(schedule)):
      if (schedule[i][1] == "R"):
         reader = schedule[i]

         previous_writers = [s for s in schedule[0:i] if s[0] != reader[0] and s[1] == "W" and s[2] == reader[2]]
         next_writers = [s for s in schedule[i+1:] if s[0] != reader[0] and s[1] == "W" and s[2] == reader[2]]
         last_previous_writer = previous_writers[-1]

         # adicione Ti --0-> Tj se Tj lê um dado produzido por Ti.
         g.add_edge(last_previous_writer[0], reader[0], 0)

         writers = next_writers
         if (len(previous_writers) >= 2): writers += previous_writers[0:-1]

         # print(f"{reader} {last_previous_writer}: {writers}")
         for writer in writers:
            if writer[0] != "b":
               # Ti: last_previous_writer
               # Tj: reader
               # Tk: writer

               # se Ti == Tb e Tj != Tf, insira Tj --0 -> Tk
               if last_previous_writer[0] == "b" and reader[0] != "f":
                  g.add_edge(reader[0], writer[0], 0)

               # se Ti != Tb e Tj == Tf, insira Tk --0-> Ti
               if last_previous_writer[0] != "b" and reader[0] == "f":
                  g.add_edge(writer[0], last_previous_writer[0], 0)

               #  se Ti != Tb e Tj != Tf, insira arestas Tk --p-> Ti ou Tj --p-> Tk
               if last_previous_writer[0] != "b" and reader[0] != "f":
                  optional_edges.append([
                     (writer[0], last_previous_writer[0]),
                     (reader[0], writer[0])
                  ])

   for p in range(len(optional_edges)):
      e1, e2 = optional_edges[p]

      g.add_edge(e1[0], e1[1], p+1)
      if (g.is_cyclic()):
         g.remove_edge(e1[0], e1[1], p+1)
         print(f"Aresta removida: T{e1[0]} -{p+1}-> T{e1[1]}")
      else:
         print(f"Aresta removida: T{e2[0]} -{p+1}-> T{e2[1]}")
         continue

      g.add_edge(e2[0], e2[1], p+1)
      if (g.is_cyclic()):
         return f"A escala não é serializável na visão, pois o grafo de precedência rotulado é cíclico\n{g}"

   ts = g.topo_sort()
   ts = [f"T{t}" for t in ts if t not in ['b', 'f']]
   return f"Grafo de precedência rotulado:\n{g}\nA escala é serializável na visão, pois o grafo de precedência rotulado é acíclico.\nUma escala serial equivalente é {ts}."

if __name__ == "__main__":
   # schedule: lista de instruções, dada na ordem em que são executadas. cada instrução é composta por 3 caracteres: o número da transação, se é R (read) ou W (write), e o item de dado, respectivamente.
   schedule_L2 = ['2RA', '2RB', '2WA', '3RA', '2WB', '1RB', '3WA', '1WB',
                  '4RB', '1RA', '4WB', '1RC', '1WA', '4RA', '4WA', '1WC']

   # print(TO_test(schedule_L2))
   # print(conflict_serializability_test(schedule_L2))
   # print(view_serializability_test(schedule_L2))
   # print(TO_test(['2RA', '1RB', '1WB', '2RB', '1RA', '1WA']))
   # print(TO_test(['2RB', '1RB', '1WB', '2RA', '1RA', '1WA']))
   # print(conflict_serializability_test(["3WY", "2RY", "1WX", "2RX", "3WX", "4RX", "5WX"]))
   # print(view_serializability_test(['3WY', '2RY', '1WX', '2RX', '3WX', '4RX', '5WX']))
   # print(view_serializability_test(['0RQ', '1WQ', '2RQ', '0WQ', '2WQ']))
   # print(view_serializability_test(['0RQ', '1WQ', '0WQ', '2WQ']))

