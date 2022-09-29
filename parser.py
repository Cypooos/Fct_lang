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
class UnknowLitteral (Exception):
  pass
class UnclosedBrackets (Exception):
  pass



def find_next_brackets(string,open,close):
  counter = 0 
  for x in range(len(string)):
    if string[x] == open:counter += 1
    elif string[x] == close: counter -= 1
    if counter == 0:
      return x
  return 0


class ConfigParser:

  STACK_LIMIT = 300 # t_lim = 333

  def __init__(self):
    self.ctx = 0
    self.path = []

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
        x_ = r_(x)
        r = v(x_)
      return r
    
    def map_(li,expr):
      r = []
      for x in v(li):
        r.append(v(v(expr)(x)))
      return r
    
    def filter_(li,expr):
      r = []
      for x in v(li):
        if v(v(expr)(x)): r.append(x)
      return r
    
    def eq(a,b):
      print("  "*self.ctx+"testing",v(a),"==",v(b),"(so result is",v(a)==v(b),")")
      return v(a) == v(b)



    # defaults are lambda-defined
    self.vars = {
      # classic
      "id":lambda x:x,
      "cste": lambda a: lambda b:v(a),
      "if": lambda test: lambda a: lambda b: v(a) if v(test) else v(b),
      "=":lambda a: ("a","="), # commentary

      # test tests
      "__evaluate_with_1":lambda fct: v(v(fct)(1)),
      "__evaluate_with_two_1s":lambda fct: v(v(v(fct)(1))(1)),

      # test conditions
      "eq": lambda a: lambda b: eq(a,b),
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
      "e_list": [],
      "append": lambda a: lambda b: v(a)+[v(b)],
      "len":lambda x: len(v(x)),
      "index": lambda a: lambda b: v(a)[v(b)],
      "range": lambda a: lambda b: [x for x in range(v(a),v(b))],

      # list global operations
      "collect": lambda li: lambda default: lambda expr: collect_(li,default,expr),
      "filter": lambda li: lambda cond: filter_(li,cond),
      "map": lambda li: lambda expr: map_(li,expr),

      # bools
      "true": True,
      "false": False,
      "and": lambda a: lambda b: v(a) and v(b),
      "or": lambda a: lambda b: v(a) or v(b),
      "not": lambda a: not v(a),
      
    }

  def get_expr(self,string):
    act_path = ""
    search_paths = [""]
    for x in self.path:
      search_paths.append(search_paths[-1]+x+".")
    
    print("  "*self.ctx+"searching for",string,"in paths",search_paths[::-1])

    for path in search_paths[::-1]:
      if path+string in self.vars.keys():
        return self.vars[path+string]
    try: return int(string)
    except ValueError:
      pass
      raise UnknowLitteral

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
        for key,value in res[2]:
          self.vars[key] = value
        self.vars[res[0]] = val
      
      ret = self.execute(res[1])
      
      if isinstance(ret,tuple) and ret[0] != None:
        ret[2].append((res[0],val))
      
      for k,v in context_vars:
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

    print("  "*self.ctx+">> Computing `"+string+"` <<")

    self.ctx += 1
    self.rec_counter = max(self.ctx,self.rec_counter)
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
          place = find_next_brackets(string[i:],"(",")")
          # print("  "*self.ctx+"Finding closed at",place,"for",string[i:])
          if place != 0:
            result = self.exec(result,self.execute(string[i+1:i+place]))
            i += place
          else:
            raise UnclosedBrackets()
        
        elif char == "[": # if we have a delayed expression
          
          if data != "":result = self.exec(result,self.get_expr(data))
          data = ""
          place = find_next_brackets(string[i:],"[","]")
          if place != 0:
            result = self.exec(result,(None,(string[i+1:i+place])))
            i += place
          else:
            raise UnclosedBrackets()
        
        elif char == "{":
          
          if data != "":result = self.exec(result,self.get_expr(data))
          data = ""
          self.path.append("INNER")
          print("  "*self.ctx,"Executing block in ctx:",".".join(self.path))

          place = find_next_brackets(string[i:],"{","}")
          if place != 0:
            self.parse(string[i+1:i+place])
            del self.path[-1]
            result = self.exec(result,self.get_expr("INNER"))
            i += place
          else:
            raise UnclosedBrackets()
          


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
          print("  "*self.ctx + "End of fetching variables for fct:`"+data+"`")

          place = find_next_brackets(string[i:],"(",")")
          if place != 0:
            print("  "*self.ctx + "Applying custom fct to result (execute)")
              
            fct_data = (data,string[i+1:i+place],[]) # context
            result = self.exec(result,fct_data)
            data = ""
            i += place
            state = "normal"
            break
          else:
            raise UnclosedBrackets
        elif char == "{":
          print("  "*self.ctx + "End of fetching variables for block:`"+data+"`")

          place = find_next_brackets(string[i:],"{","}")
          if place != 0:
            print("  "*self.ctx + "Applying custom fct to result (execute)")
              
            fct_data = (data,string[i:i+place+1],[]) # context
            result = self.exec(result,fct_data)
            data = ""
            i += place
            state = "normal"
            break
          else:
            raise UnclosedBrackets
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


  def parse(self,string):

    # state in ["clef", "val","clefC", "valC"]
    
    state = "clef"
    i = 0
    self.path.append("")
    while i <len(string):
      char = string[i]


      if state == "clef":
        if char == "=":
          state = "val"
          self.path.append("")
        elif char == "{":
          self.path.append("")
        elif char == "}":
          del self.path[-1]
          self.path[-1] = ""
        elif char == "#":
          state="clefC"
        else:
          self.path[-1]+=char
      
      elif state == "clefC":
        if char == "#" or char == "\n":state = "clef"
      elif state == "val":
        if char == "{":
          place = find_next_brackets(string[i:],"{","}")
          if place != 0:
            self.path[-1] += string[i:i+place+1]
            i += place
          else:
            raise UnclosedBrackets

        elif char == ";":
          self.path = list(filter(lambda x: x != "", [ x.strip() for x in self.path]))
          self.path,code = self.path[:-1],self.path[-1]
          state = "clef"
          path_str = ".".join(self.path)

          print("  "*self.ctx +"\n --- New Key ---\nSetting `"+path_str+"`")
          self.rec_counter = 0
          self.vars[path_str] = self.execute(code)
          print("  "*self.ctx +"Key added. rec_counter="+str(self.rec_counter)+"\n")
          self.path[-1] = ""
        elif char == "}":
          del self.path[-1]
          self.path[-1] = ""
        elif char == "#":
          state = "valC"
        else:
          self.path[-1]+= char
      elif state == "valC":
        if char == "#" or char == "\n":state = "val"
       
      i+= 1 
    print(vars)



  def start(self):
    print("\n".join([k+":"+str(v) for k,v in self.vars.items()]))
    pass