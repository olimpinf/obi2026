#!/bin/bash

school=$1



# iniciacao

psql -d obi2020 -U obi -c "update compet set compet_classif_fase2=True where compet_school_id=${school} and compet_type=7 and compet_points_fase2>=10;"

psql -d obi2020 -U obi -c "update compet set compet_classif_fase2=True where compet_school_id=${school} and compet_type=1 and compet_points_fase2>=11;"

psql -d obi2020 -U obi -c "update compet set compet_classif_fase2=True where compet_school_id=${school} and compet_type=2 and compet_points_fase2>=13;"


# programacao

psql -d obi2020 -U obi -c "update compet set compet_classif_fase2=True where compet_school_id=${school} and compet_type=5 and compet_points_fase2>=120;"

psql -d obi2020 -U obi -c "update compet set compet_classif_fase2=True where compet_school_id=${school} and compet_type=3 and compet_points_fase2>=100;"

psql -d obi2020 -U obi -c "update compet set compet_classif_fase2=True where compet_school_id=${school} and compet_type=4 and compet_points_fase2>=120;"

