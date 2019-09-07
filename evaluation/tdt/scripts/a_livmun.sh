script /home/memonick/evaluation/tdt/out/a_livmun_ful_eld_graph.txt \
-c 'python3 implementation/split_accelerated_eld.py LIVMUN_FUL ELD Graph'

script /home/memonick/evaluation/tdt/out/a_livmun_ful_eld_fmmr.txt \
-c 'python3 implementation/split_accelerated_eld.py LIVMUN_FUL ELD FMMR'

script /home/memonick/evaluation/tdt/out/a_livmun_apd_eld_graph.txt \
	-c 'python3 implementation/split_accelerated_eld.py LIVMUN_APD ELD Graph'

script /home/memonick/evaluation/tdt/out/a_livmun_apd_eld_fmmr.txt \
	-c 'python3 implementation/split_accelerated_eld.py LIVMUN_APD ELD FMMR'

script /home/memonick/evaluation/tdt/out/a_livmun_eld_graph.txt \
	-c 'python3 implementation/split_accelerated_eld.py LIVMUN ELD Graph'

script /home/memonick/evaluation/tdt/out/a_livmun_eld_fmmr.txt \
	-c 'python3 implementation/split_accelerated_eld.py LIVMUN ELD FMMR'
