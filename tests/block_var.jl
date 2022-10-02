

List {

    empty_list : empty;

    # create a range of int from a to b
    range : \a(\b(
        if (gt a b) empty_list
        (couple a (range (add a 1) b))
    ));

    # like Ocaml's List.map
    map : \list(\fct(
        if (list eq empty_list) empty_list
        (couple (fct (fst list)) (map (snd list) fct))
    ));

    # like Ocaml's collect
    collect : \list(\fct(\default({
        : if (eq list empty_list) default
        (fct (collect (snd list) fct default) (fst list));
    })));

    maxi : \list(collect list (\r(\e(max e r))) (fst list));
    mini : \list(collect list (\r(\e(min e r))) (fst list));

}


Tests {
    
    List.range {
        ordonned  : List.range 0 1;
        ordonned1 : List.range 11 10; 
        ordonned2 : List.range -11 2; 
    }
    List.map {
        map1 : List.map (List.range 0 10) \n(add n 1);
        map2 : List.map (List.range 0 10) \n(mul n 10);
    }

    random_list : List.map (List.range 0 23) \n(mod (mul n 7) 23);
    
    # List.collect {
    #     max1 : List.maxi (List.range 0 20);
    #     max2 : List.maxi random_list;
    # }
}
