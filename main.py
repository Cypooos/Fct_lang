from parser import ConfigParser, StackOverflow



def main():

  psr = ConfigParser("config")
  try:
    psr.parse()
  except StackOverflow:
    print("\n\nCUSTOM STACK OVERFLOW!")
  psr.start()



if __name__=='__main__':main()