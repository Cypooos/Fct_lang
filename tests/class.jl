global : 999;

# test for the path system (accesing out-of-scope values)

a {
  b {
    test:9;
    c {
      test : add b.test 1;
    }
  }
  b2{
    test:99;
    c{
      test:add b.test 1;
      test2:add b2.test 1;
      test3:add global 1;
    }
    c2 : add global 1;
  }
}

test : add a.b2.c.test 90; # 100

# test for context-passed value
late {
  a : 1;
  b : \n(add a n);
}

test2 : late.b 3; # 4