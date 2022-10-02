# --- Recursives test ---

# self-calling 1-depth recursive fct
rec_1 : \a(\b(if (eq a 1) 0 (rec_1 1 2)));
rec_1_test : rec_1 10 20;

# should be impossible -> it will evaluate "rec_2" while it doesn't yet exist
# rec_2 : add rec_2 1;

# Test of recursive function definition -> doesn't evaluate the expression
rec_3 : \n(rec_4 0);



# self-calling b-deapth recursive fct
rec_4 : \a(if (eq a 0) (1) (rec_4 (sub a 1)));
rec_4_test : rec_4 3;


# self-calling b-deapth recursive fct of 2 variables
rec_5 : \a(\b(if (eq a 0) (1) (rec_5 (sub a 1) 0)));
rec_5_test : rec_5 3 0;

# Count all integers from a to b
rec_6 : \a(\b(if (gt a b) (0) (add 1 (rec_6 (add a 1) b))));
rec_6_test : rec_6 3 4;