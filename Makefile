D2 ?= d2
D2_FILES := $(wildcard *.d2)
SVG_FILES := $(D2_FILES:.d2=.svg)

.PHONY: all clean

all: $(SVG_FILES)

%.svg: %.d2
	$(D2) $< $@

clean:
	rm -f $(SVG_FILES)
