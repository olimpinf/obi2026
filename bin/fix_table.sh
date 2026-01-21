#!/bin/sh

sed -i "~" "s/\<table border=\"0\" cellpadding=\"4\" cellspacing=\"0\" width=\"100\%\"\>/\<table class=\"simple\"\\>/" $1


