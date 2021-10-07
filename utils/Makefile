P4_INCLUDE_PATH = ./utils/p4include
P4C = petr4
P4C_ARGS += typecheck -I $(P4_INCLUDE_PATH)

RUN_SCRIPT = ./utils/run_exercise.py

SOURCE = $(wildcard *.p4)

RUN_ARGS += -f $(SOURCE)
RUN_ARGS += -I $(P4_INCLUDE_PATH)

all: run

run: build
	sudo python $(RUN_SCRIPT) -t $(TOPO) $(RUN_ARGS)

stop:
	sudo mn -c

build:
	$(P4C) $(P4C_ARGS) $(SOURCE)

controller:
	PYTHONPATH=../utils python3 $(CONTROLLER)

clean: stop
	rm -f *.pcap
	rm -rf $(BUILD_DIR) $(PCAP_DIR) $(LOG_DIR)
