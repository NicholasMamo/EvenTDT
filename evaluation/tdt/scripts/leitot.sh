script /home/memonick/evaluation/tdt/out/leitot_apd_eld_graph.txt \
	-c 'python3 implementation/split_accelerated_eld.py LEITOT_APD ELD Graph'

script /home/memonick/evaluation/tdt/out/leitot_apd_eld_fmmr.txt \
	-c 'python3 implementation/split_accelerated_eld.py LEITOT_APD ELD FMMR'

script /home/memonick/evaluation/tdt/out/leitot_eld_graph.txt \
	-c 'python3 implementation/split_accelerated_eld.py LEITOT ELD Graph'

script /home/memonick/evaluation/tdt/out/leitot_eld_fmmr.txt \
	-c 'python3 implementation/split_accelerated_eld.py LEITOT ELD FMMR'

script /home/memonick/evaluation/tdt/out/leitot_ful_eld_graph.txt \
	-c 'python3 implementation/split_accelerated_eld.py LEITOT_FUL ELD Graph'

script /home/memonick/evaluation/tdt/out/leitot_ful_eld_fmmr.txt \
	-c 'python3 implementation/split_accelerated_eld.py LEITOT_FUL ELD FMMR'
