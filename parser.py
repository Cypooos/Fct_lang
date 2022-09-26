#  
#  nom= expression;;
#  nom= expression;;
#  emission { clé=valeur;clé=valeur;clé=valeur};
#  ________________________________________
#  
#  CHAR := [a-zA-Z0-9_@!%]*
#  LETTERS := [a-zA-Z_@!%]*
#  nom := <LETTERS><CHAR>*
#  expression := nom | \ nom ... nom ( expression ) | expression expression
#  ________________________________________

from textwrap import shorten


class StackOverflow (Exception):
  pass

class ConfigParser:

  STACK_LIMIT = 50

  def __init__(self,file):
    self.file = file
    f = open(file,"r")
    self.content = f.read()
    self.ctx = 0

    # A fonction is either a tuple (argument, code) or a lambda expression for defaults / optimized one
    
    # In case an argument is a delayed expression / function, we need the real argument / as a lambda python function
    def v(x):
      if isinstance(x, tuple) and x[0] == None:
        return self.execute(x[1])
      elif isinstance(x,tuple):
        return lambda t: self.exec(x,t)
      else: return x
    
    def collect_(li,default,expr):
      r = v(default)
      for x in v(li):
        x = v(x)
        expr_ = v(expr)
        r_d = expr_(r)
        r_ = v(r_d)
        print("IN FOR X:",x,'TYPE:',type(x))
        print("IN FOR R_:",r_,'TYPE:',type(r_))
        x_ = r_(x)
        r = v(x_)
        print("  "*self.ctx+"for, x:",x,"and r:",r)
      return r
    
    def iter_(li,expr):
      r = []
      for x in v(li):
        r.append(v(v(expr)(x)))
        print("  "*self.ctx+"iter, x =",x,"r =",r)
      return r
    
    def filter_(li,expr):
      r = []
      for x in v(li):
        if v(v(expr)(x)): r.append(x)
        print("  "*self.ctx+"filter, x =",x,"r =",r)
      return r


    # defaults are lambda-defined
    self.vars = {
      # classic
      "id":lambda x:x,
      "cste": lambda a: lambda b:v(a),
      "if": lambda test: lambda a: lambda b: v(a) if v(test) else v(b),

      # test test
      "__evaluate_with_1":lambda fct: v(v(fct)(1)),
      "__evaluate_with_two_1s":lambda fct: v(v(v(fct)(1))(1)),

      # test conditions
      "eq": lambda a: lambda b: v(a) == v(b),
      "ls": lambda a: lambda b: v(a) < v(b),
      "le": lambda a: lambda b: v(a) <= v(b),
      "gt": lambda a: lambda b: v(a) > v(b),
      "ge": lambda a: lambda b: v(a) >= v(b),
      
      # int
      "add": lambda a: lambda b: v(a)+v(b),
      "sub": lambda a: lambda b: v(a)-v(b),
      "mul": lambda a: lambda b: v(a)*v(b),
      "div": lambda a: lambda b: v(a)//v(b),
      "mod": lambda a: lambda b: v(a)%v(b),
      "max": lambda a: lambda b: max(v(a),v(b)),
      "min": lambda a: lambda b: min(v(a),v(b)),
      
      # cvrt
      "int":lambda a: int(v(a)),
      "flt": lambda a: float(v(a)),
      "str": lambda a: str(v(a)),

      # usual list functions
      "t_list": lambda a: [v(a)],
      "append": lambda a: lambda b: v(a).append(v(b)),
      "index": lambda a: lambda b: v(a)[v(b)],
      "range": lambda a: lambda b: [x for x in range(v(a),v(b))],

      # list global operations
      "collect": lambda li: lambda default: lambda expr: collect_(li,default,expr),
      "filter": lambda li: lambda cond: filter_(li,cond),
      "iter": lambda li: lambda expr: iter_(li,expr),

      # bools
      "true": True,
      "false": False,
      "and": lambda a: lambda b: v(a) and v(b),
      "or": lambda a: lambda b: v(a) or v(b),
      "not": lambda a: not v(a),
      
    }
    f.close()

  def get_expr(self,string):
    if string in self.vars.keys():
      return self.vars[string]
    else:
      try: return int(string)
      except ValueError:pass

  # use to evaluate `res` with a value `val`
  def exec(self,res,val):

    if callable(res):
      return res(val)

    elif isinstance(res, tuple):

      if res[0] == None:
        print("  "*self.ctx+"Delayed expression executed as it takes an argument")
        context_vars = []

      else:
        print("  "*self.ctx+"setting",res[0],":=",val,"for evalating `"+res[1]+"` with param ",res[2])
        context_vars = [(key,self.vars.get(key,None)) for key,_ in res[2]]
        context_vars.append((res[0],self.vars.get(res[0],None)))
        self.vars[res[0]] = val
        for key,value in res[2]:
          self.vars[key] = value
      
      ret = self.execute(res[1])
      
      if isinstance(ret,tuple) and ret[0] != None:
        ret[2].append((res[0],val))
      
      for k,v in context_vars:
        print(k,v)
        if v == None: del self.vars[k]
        else:self.vars[k] = v
    
      print("  "*self.ctx+"Applying complete")
      return ret
    else:
      print("  "*self.ctx+"/!\ Applying",val,"on non callable result `"+str(res)+"`, assuming cste")
      return res

  def execute(self,string):

    string = " ".join(string.split()) # to remove if strings are added as a default object
    string += " "
    shorten = string if len(string) <= 40 else string[:40]+"..."

    print("  "*self.ctx+">> Computing `"+shorten+"` <<")

    self.ctx += 1
    if self.ctx >= self.STACK_LIMIT:
      raise StackOverflow
    
    result = lambda x : x
    state = "normal"
    data = ""
    i = 0

    while i < len(string):

      char = string[i]
      data = data.strip()
      
      if state == "normal":
        if char == "(": # if we have a subexpression
          
          if data != "":result = self.exec(result,self.get_expr(data))
          data = ""
          counter = 0 # find the end of the opening brakets
          for x in range(i,len(string)):
            if string[x] == "(":counter += 1
            elif string[x] == ")": counter -= 1
            if counter == 0:
              result = self.exec(result,self.execute(string[i+1:x]))
              i = x
              break
        
        elif char == "[": # if we have a delayed expression
          
          if data != "":result = self.exec(result,self.get_expr(data))
          data = ""
          counter = 0 # find the end of the opening brakets
          for x in range(i,len(string)):
            if string[x] == "[":counter += 1
            elif string[x] == "]": counter -= 1
            if counter == 0:
              result = self.exec(result,(None,(string[i+1:x])))
              i = x
              break
        
        # end of current fetching and evaluation of result
        elif char == " " and data != "" :
          
          result = self.exec(result,self.get_expr(data))
          data = ""
        
        # beginning of creating a fonction, also an end of the current fetching 
        elif char == "\\":
          print("  "*self.ctx + "Fetching linkable variables...")
          
          if data != "":result = self.exec(result,self.get_expr(data))
          data = ""
          
          state = "link"
        else:data += char
      
      elif state == "link":
        # end of the fetching for the variable's name
        if char == "(":
          print("  "*self.ctx + "End of fetching variables:`"+data+"`")
          counter = 0 # find the end of the opening brakets
          for x in range(i,len(string)):
            if string[x] == "(":counter += 1
            elif string[x] == ")": counter -= 1
            if counter == 0:
              
              print("  "*self.ctx + "Applying custom fct to result (execute)")
              
              fct_data = (data,string[i+1:x],[]) # context
              result = self.exec(result,fct_data)
              data = ""
              i = x
              state = "normal"
              break
        else:
          data += char
      i+=1
    
    if isinstance(result,tuple) and result[0] == None:
      print("  "*self.ctx+"Delayed expression executed as it is the last remaning one")
      result = self.execute(result[1])
    shorten = str(result) if len(str(result)) <= 40 else str(result)[:40]+"..."
    print("  "*self.ctx + "Result is: `"+shorten+"`")
    self.ctx -= 1
    return result


  def parse(self):

    # states = ["nom", "val>expression","clé>expression","clé"]
    
    state = "nom"
    data = [""]
    for char in self.content:

      if state == "nom":
        if char == "=":
          state = "val>expression"
          data.append("")
        elif char == "{":
          state = "clé"
          data.append("")
        else:
          data[-1]+=char
      
      elif state == "val>expression":
        if char == ";":
          data = [ x.strip() for x in data]
          state = "nom"

          if data[0] == "":
            print("Empty key ignored\n")
          else:
            print("\n --- New Key ---\nSetting `"+str(data[0])+"`")
            self.vars[data[0]] = self.execute(data[-1])
            print("Key added.\n")
          data = [""]
        else:
          data[-1]+= char
        

      elif state == "clé>expression":
        if char == ";":

          data = [ x.strip() for x in data]
          state = "clé"
          if data[1] == "":
            print("Empty key ignored.\n")
          else:
            print("\n --- New Emm Key ---\nSetting `"+data[0]+"."+data[1]+"`")
            self.vars[data[0]+"."+data[1]] = self.execute(data[-1])
            print("Emm Key added.\n")
          data[-1] = ""
        else:
          data[-1]+= char
      
      elif state == "clé":
        if char == "=":
          print("clé->=")
          state = "clé>expression"
          data.append("")
        elif char == "}":
          print("clé->}")
          data = [""]
          state = "nom"
        else:
          data[-1]+=char
    
      else:raise Exception("Unknow State in Config Parser")
    print(vars)



  def start(self):
    print("\n".join([k+":"+str(v) for k,v in self.vars.items()]))
    pass