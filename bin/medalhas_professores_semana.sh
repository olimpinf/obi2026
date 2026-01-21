!# /bin/bash

for i in `seq 2000 2024` ; do echo $i ; psql -d obi$i -U obi -c "select count(*) from compet where compet_medal in ('o','p','b') and compet_name in ('Arthur Lobo Leite Lopes','Juliana Borin','Pedro César Mesquita Ferreira','Enzo Dantas','Daniel Yuji Hosomi','Thiago Mota Martins','André Amaral de Sousa','Arthur Lobo Leite Lopes','Arthur Ferreira do Nascimento','Caique Paiva','Filipe de Souza Lalic','Leonardo Valente Nascimento','Luana Amorim','Mateus Bezrutchka','Naim Shaikhzadeh Santos','Pedro Henrique Assunção','Rafael Nascimento Soares');"; done

