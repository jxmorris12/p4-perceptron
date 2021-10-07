import sys
sys.path.append('./utils')

from petr4 import App
from petr4.runtime import *
from topo import *
from tornado.ioloop import *

class Controller(App):
  def init_topo(self):
    topo = Topology()

    # add switches
    topo.add_switch("s1")

    # add hosts (IP and MAC addresses in decimal)
    topo.add_host("h1", "167772417", "8796093022481")

    # add links between hosts and switch
    topo.add_link("h1", "s1", 0, 1, 1)
        
    # compute shortest paths
    paths = topo.e2e_shortest_paths()
    self.topo = topo
    self.paths = paths
    
  def __init__(self, port=9000):
    super().__init__(port)
    self.init_topo()
    
  def switch_up(self, switch, ports):                 
    print(f"{switch} is up!")
    # do lookup tables here if I need to
    return

app = Controller()
app.start()
