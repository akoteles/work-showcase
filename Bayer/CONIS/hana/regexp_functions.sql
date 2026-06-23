
     SELECT substring_regexpr('\b\w+(?<!input)\b' FLAG 'i' in t.txt
                              FROM LOCATE_REGEXPR('\b\w+[input]\b' FLAG 'i' in t.txt
                                                   OCCURRENCE  OCCURRENCES_REGEXPR('\b\w+[input]\b' FLAG 'i' in t.txt)-2
                                                 )
                              )
      from (select 'a1b2 input dasdads input rrerere input xxxdsadasxx' txt
              from dummy
           ) t;
