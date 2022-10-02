from parser import ConfigParser, StackOverflow, UnclosedBrackets

def main():

  psr = ConfigParser()
  try:
    file = "tests/rec.jl"
    
    f = open(file,"r")
    content = f.read()
    f.close()

    psr.parse(content)
  except StackOverflow:
    print("\n\nCUSTOM STACK OVERFLOW!")
  except UnclosedBrackets:
    print("\n\nCUSTOM UNCLOSED BRACKETS ERROR!")
  psr.start()



if __name__=='__main__':main()