CHOWN = /usr/bin/chown
CHMOD = /usr/bin/chmod
EXEC = mr_writer

all: $(EXEC)
	-$(SILENT) $(CHOWN) root:root $(EXEC)
	-$(SILENT) $(CHMOD) 4755 $(EXEC)
    
clean:
	rm -f $(EXEC)
