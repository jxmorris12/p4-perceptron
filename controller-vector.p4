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
    #
    # 'delta' table
    #
    # *** STATE 0: Haven't seen anything we want yet ***
    for code in range(0,256):
      # allow strings 'I' and 'P4'
      if code == ord('I'):
        # 'I' goes directly to "accept"
        next_state = "2"
      elif code == ord('P'):
        next_state = "1"
      else:
        next_state = "0"
      entry = Entry(
        "delta", [
          ("hdr.regex.state", "0"), 
          ("hdr.regex.code", str(code))
        ], 
        "goto", [
          ("next_state", next_state)
        ]
      )
      self.insert(switch, entry)
      entry2 = Entry(
        "delta2", [
          ("hdr.regex.state", "0"), 
          ("hdr.regex.code", str(code))
        ], 
        "goto", [
          ("next_state", next_state)
        ]
      )
      self.insert(switch, entry2)
    # *** STATE 1: We have seen a 'P' ***
    for code in range(0,256):
      if code == ord('4'):
        next_state = "2"
      else:
        next_state = "0"
      entry = Entry(
        "delta", [
          ("hdr.regex.state", "1"), 
          ("hdr.regex.code", str(code))
        ], 
        "goto", [
          ("next_state", next_state)
        ]
      )
      self.insert(switch, entry)
      entry2 = Entry(
        "delta2", [
          ("hdr.regex.state", "1"), 
          ("hdr.regex.code2", str(code))
        ], 
        "goto", [
          ("next_state", next_state)
        ]
      )
      self.insert(switch, entry2)
    # *** STATE 2: We have seen 'I' or 'P4' ***
    for code in range(0,256):
      # continuously redirect to "2"
      entry = Entry(
        "delta", [
          ("hdr.regex.state", "2"), 
          ("hdr.regex.code", str(code))
        ], 
        "goto", [
          ("next_state", "2")
        ]
      )
      self.insert(switch, entry)
      # continuously redirect to "2"
      entry2 = Entry(
        "delta2", [
          ("hdr.regex.state", "2"), 
          ("hdr.regex.code2", str(code))
        ], 
        "goto", [
          ("next_state", "2")
        ]
      )
      self.insert(switch, entry2)
    #
    # 'final' table
    #
    # *** State 0 -> reject ***
    entry = Entry(
      "final", [
        ("hdr.regex.state", "0")
      ], 
      "reject", []
    )
    self.insert(switch, entry)
    # *** State 1 -> reject ***
    entry = Entry(
      "final", [
        ("hdr.regex.state", "1")
      ], 
      "reject", []
    )
    self.insert(switch, entry)
    # *** State 2 -> accept ***
    entry = Entry(
      "final", [
        ("hdr.regex.state", "2")
      ], 
      "accept", []
    )
    self.insert(switch, entry)
    return

app = Controller()
app.start()
