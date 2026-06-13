// Expressão de encapsulamento para o PostgREST do Supabase
{{ "in.(\"" + $json.TEMAS_MONITORADOS.replace(/,/g, '","') + "\")" }}