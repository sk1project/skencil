

all:


LINGUAS = de
MO_DIR = ../Resources/Messages
PO_DIR = po
DOMAIN = skencil

POTFILES:
	grep -l "_(\"\\|\"\"'\\|''\"" \
	../Sketch/*.py ../{Sketch,Plugins}/*/*.py ../Script/*.py > POTFILES

POPACKAGE = skencil

pot: POTFILES
	xpot -o $(DOMAIN).pot `cat POTFILES`
	#xgettext -k_ -o $(DOMAIN).pot `cat POTFILES`

update-po:
	for po in *.po; do \
		lingua=`basename $$po .po`; \
	        mv $$lingua.po $$lingua.old.po; \
		if msgmerge -o $$lingua.po $$lingua.old.po $(DOMAIN).pot; then\
		    rm $$lingua.old.po; \
		else \
		    rm -f $$lingua.po; \
		    mv $$lingua.old.po $$lingua.po; \
		fi \
	done


mo:
	for po in *.po; do\
		lingua=`basename $$po .po`; \
		install -d $(MO_DIR)/$$lingua/LC_MESSAGES/ ; \
		echo -n $$po": "; \
		msgfmt --statistics \
			-o $(MO_DIR)/$$lingua/LC_MESSAGES/$(DOMAIN).mo $$po ;\
	done


