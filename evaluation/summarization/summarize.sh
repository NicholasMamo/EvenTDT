#!/bin/bash

export PERL5LIB=$PATH:~/evaluation/summarization/mead/bin/addons/formatting
export LC_CTYPE=en_US.UTF-8
export LC_ALL=en_US.UTF-8

python3 generate_mead.py $1
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P ) # get the script path
echo $parent_path
cd "/mnt/evaluation/summarization/mead_files/$1" # go to the summary folder

for dir in */; do
	./../../mead/bin/addons/formatting/text2cluster.pl $dir
	./../../mead/bin/mead.pl -o "$dir/summary.txt" -output_mode summary -w -a 50 ${dir%/}
	# ./../../mead/bin/mead.pl -o "$dir/summary.txt" -s -a 3 -meadrc ${parent_path}/mead/.meadrc ${dir%/}
	# ./../../mead/bin/mead.pl -classifier "default-classifier.pl Length 9 Centroid 1 Position 1 SimWithFirst 1" -w -a 100 ${dir%/}
	cat "$dir/summary.txt" | sed -r "s/^\[[0-9]+?]  //i" > "$dir/clean_summary.txt" # remove the sentence numbers
done

cd $parent_path
python3 print_combined_mead.py $1
