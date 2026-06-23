select substring_regexpr('\b\w{4,}+(?<!input)\b' FLAG 'i' in 'WITH n AS input, OCB AS VarCreatedBy, ' FROM 11 ) from dummy;
