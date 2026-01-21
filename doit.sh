#sed -i~ 's/\<fieldset\>/\<fieldset class="border p-2"\>/' $1

#sed -i~ 's/\<legend\>/\<legend class="float-none w-auto p-2"\>/' $1

#sed -i~ 's/\<button type="submit" class="button"\>/\<button type="submit" class="btn btn-primary mt-4"\>/' $1

#sed -i~ 's/base_docs.html/\base_two_columns.html/' $1

#sed -i~ 's/a class=\"myButton\"/a class=\"btn btn-primary\" role=\"button\"/' $1

#sed -i~ 's/\/static\/img/\/static\/assets\/img/' $1

#sed -i~ 's/\<table class=\"simple\"\>/\<table class=\"table table-sm table-striped table-bordered\"\>\n  \<thead class="table-primary"\>/' $1

# only the first ocurrence
#sed -e '1 s/\<\/tr\>/\<\/thead\>\n\<\/tr\>/; t' -i~ -e '1,// s//\<\/thead\>\n\<\/tr\>/' $1

#sed -i~ 's/^\<h1\>/<\!--\<h1\>/' $1
#sed -i~ 's/\<\/h1\>$/\<\/h1\> --\>/' $1
