class Emission:

  def __init__(self,id,**config):
    self.id = id
    self.config = config

  def get_prog(self,date):
    return ("Err","Phosphorus - 1",date+10)
  
  def on_frame(self):
    self.config.get("on_frame", lambda x:())

  def on_play(self):
    self.config.get("on_play", lambda x:())