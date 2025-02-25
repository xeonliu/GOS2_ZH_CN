all: pack_script pack_font
	
pack_script: apply
	python ./hello.py 'e:/PSP_GAME/USRDIR/SCRIPT.THFS' -f ./chs_translated/ -o SCRIPT.THFS -m repack

apply: table all_mappings.json jpn 
	python ./apply.py

jpn:
	python ./hello.py 'e:/PSP_GAME/USRDIR/SCRIPT.THFS' -o jpn -m unpack

jpn_font:
	python ./hello.py 'e:/PSP_GAME/USRDIR/FONT.THFS' -o jpn_font -m unpack

table: all_mappings.json jpn_font
	python ./dict.py

pgf_font: ./pgftool/ttf_pgf ./pgftool/mix_pgf ./pgftool/dump_pgf
	./pgftool/ttf_pgf wqy-microhei.ttc wqy.PGF
	cp jpn_font/JAP8.PGF chs_font/
	./pgftool/mix_pgf chs_font/JAP8.PGF wqy.PGF
	./pgftool/dump_pgf -h chs_font/JAP8.PGF

./pgftool/ttf_pgf ./pgftool/mix_pgf ./pgftool/dump_pgf: 
	cd pgftool && make

pack_font: jpn_font pgf_font table
	cp jpn_font/ucs2jis.bin chs_font/
	python ./hello.py 'e:/PSP_GAME/USRDIR/FONT.THFS' -f ./chs_font/ -o FONT.THFS -m repack

install:
	cp SCRIPT.THFS 'd:/EmulatorROM/gos/PSP_GAME/USRDIR/SCRIPT.THFS'
	cp FONT.THFS 'd:/EmulatorROM/gos/PSP_GAME/USRDIR/FONT.THFS'

.PHONY: jpn jpn_font chs_translated clean

clean:
	rm -f SCRIPT.THFS FONT.THFS
	rm -f jpn_font/* chs_font/*
	rm -f jpn/* chs_translated/*
	# rm -f all_mappings.json
	cd pgftool && make clean
	rm output_mapping.json