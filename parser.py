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
#  
#  states = { "name|expr", "def_expression", "key_emm", "" }
#  
#  ________________________________________
#  
#  test: \x y(add x y)
#  woua: add x \(add y z)()

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


    def if_(t,a,b):
      print("  "*self.ctx + "test "+str(t)+": "+str(a)+" <--> "+str(b))
      if t:return a
      return b
    
    # fonction = tuple (argument, code) or lambda

    # defaults are lambda
    self.vars = {
      # classic
      "id":lambda x:x,
      "cste": lambda a: lambda b:a,
      "if": lambda test: lambda a: lambda b: if_(test,a,b),
      "eq": lambda a: lambda b: a == b,
      "ls": lambda a: lambda b: a < b,
      "le": lambda a: lambda b: a <= b,
      "gt": lambda a: lambda b: a > b,
      "ge": lambda a: lambda b: a >= b,
      
      # op
      "add": lambda a: lambda b: a+b,
      "sub": lambda a: lambda b: a-b,
      "mul": lambda a: lambda b: a*b,
      "div": lambda a: lambda b: a/b,
      "mod": lambda a: lambda b: a%b,
      
      # cvrt
      "int":lambda a: int(a),
      "flt": lambda a: float(a),
      "str": lambda a: str(a),

      # lists
      "t_list": lambda a: [a],
      "index": lambda a: lambda b: a[b],
      "range": lambda a: lambda b: [x for x in range(a,b)],

      # bools
      "true": True,
      "false": False,
      "and": lambda a: lambda b: a and b,
      "or": lambda a: lambda b: a or b,
      "not": lambda a: not a,
      
    }
    f.close()

  def parse(self):

    def get_expr(string):
      if string in self.vars.keys():
        return self.vars[string]
      else:
        try: return int(string)
        except ValueError:pass

    def execute(string):
      string = " ".join(string.split()) # to remove if strings are added
      shorten = string if len(string) <= 40 else string[:40]+"..."
      print("  "*self.ctx+">> Computing `"+shorten+"` <<")

      if "n" in self.vars:print("  "*self.ctx+"n is",self.vars["n"])

      self.ctx += 1
      if self.ctx >= self.STACK_LIMIT:
        raise StackOverflow

      result = lambda x : x
      state = "normal"
      data = ""
      string += " "

      # use to evaluate "result" with a value
      def exec(val):
        nonlocal result
        if callable(result):
          result = result(val)
        elif isinstance(result, tuple):
          print("  "*self.ctx+"setting",result[0],":=",val,"for evalating `"+result[1]+"`")
          temp = self.vars.get(result[0],None)
          self.vars[result[0]] = val
          

          res = execute(result[1])
          if temp != None:
            self.vars[result[0]] = temp
          else:
            del self.vars[result[0]]
          result = res
        
          print("  "*self.ctx+"Applying complete")

        else:
          print("  "*self.ctx+"/!\ Applying",val,"on non callable result, assuming cste")


      i = 0

      while i < len(string):
        char = string[i]

        data = data.strip()

        if state == "normal":

          if char == "(": # if we have a subexpression
            
            if data != "":exec(get_expr(data))
            data = ""

            counter = 0 # find the end of the opening brakets
            for x in range(i,len(string)):

              if string[x] == "(":counter += 1
              elif string[x] == ")": counter -= 1

              if counter == 0:
                exec(execute(string[i+1:x]))
                i = x
                break


          # end of current evaluation
          elif (char == " ") and data != "" :
            
            exec(get_expr(data))
            data = ""
          # begenning of creating a fonction, also an end of the current evaluation
          elif char == "\\":
            print("  "*self.ctx + "Fetching linkable variables...")
            
            if data != "":exec(get_expr(data))
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
                
                print("  "*self.ctx + "Applying fct to result")
                fct_data = (data,string[i+1:x])
                exec(fct_data)
                data = ""
                i = x
                state = "normal"
                break
          else:
            data += char
        i+=1
      
      shorten = str(result) if len(str(result)) <= 40 else str(result)[:40]+"..."
      print("  "*self.ctx + "Result is: `"+shorten+"`")
      self.ctx -= 1
      return result


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
          print("\n --- New Key ---\nSetting `"+str(data[0])+"`")
          self.vars[data[0]] = execute(data[-1])
          state = "nom"
          data = [""]
          print("Key added.\n")
        else:
          data[-1]+= char
        

      elif state == "clé>expression":
        if char == ";":
          data = [ x.strip() for x in data]
          print("\n --- New Emm Key ---\nSetting `"+data[0]+"."+data[1]+"`")
          self.vars[data[0]+"."+data[1]] = execute(data[-1])
          state = "clé"
          data[-1] = ""
          print("Emm Key added.\n")
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