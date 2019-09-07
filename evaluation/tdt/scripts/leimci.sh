script /home/memonick/evaluation/tdt/out/leimci_apd_eld_graph.txt \
	-c 'python3 implementation/split_accelerated_eld.py LEIMCI_APD ELD Graph'

script /home/memonick/evaluation/tdt/out/leimci_apd_eld_fmmr.txt \
	-c 'python3 implementation/split_accelerated_eld.py LEIMCI_APD ELD FMMR'

script /home/memonick/evaluation/tdt/out/leimci_ful_eld_graph.txt \
	-c 'python3 implementation/split_accelerated_eld.py LEIMCI_FUL ELD Graph'

script /home/memonick/evaluation/tdt/out/leimci_ful_eld_fmmr.txt \
	-c 'python3 implementation/split_accelerated_eld.py LEIMCI_FUL ELD FMMR'

script /home/memonick/evaluation/tdt/out/leimci_eld_graph.txt \
	-c 'python3 implementation/split_accelerated_eld.py LEIMCI ELD Graph'

script /home/memonick/evaluation/tdt/out/leimci_eld_fmmr.txt \
	-c 'python3 implementation/split_accelerated_eld.py LEIMCI ELD FMMR'
