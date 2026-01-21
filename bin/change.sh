#!/bin/bash

file=$1
echo ${file}
#sed -i "~" 's/de Mérito/de Medalhas/' ${file}
#sed -i "~" 's/"..\/..\/extras\//"\/static\/extras\//' ${file}
sed -i "~" 's/school_contact_/school_deleg_/g' ${file}
