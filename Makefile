# SPDX-License-Identifier: CC0-1.0
#
# SPDX-FileContributor: Antonio Niño Díaz, 2023-2025

# Source code paths
# -----------------

SOURCEDIRS	:= source
INCLUDEDIRS	:= source

# Defines passed to all files
# ---------------------------

DEFINES		:=

# Libraries
# ---------

LIBS		:= -lcurl -ldiscord
LIBDIRS		:= $(CURDIR)/libs

# Build artifacts
# ---------------

NAME		:= $(shell basename $(CURDIR))
BUILDDIR	:= build
ELF		:= $(NAME)

# Tools
# -----

STRIP		:= -s
BINMODE		:= 755

HOSTCC		?= $(CC)
HOSTCXX		?= $(CXX)
HOSTLD		?= $(HOSTCC)
CP		:= cp
MKDIR		:= mkdir
RM		:= rm -rf
MAKE		:= make
INSTALL		:= install

# Verbose flag
# ------------

ifeq ($(VERBOSE),1)
V		:=
else
V		:= @
endif

# Source files
# ------------

SOURCES_C	:= $(shell find -L $(SOURCEDIRS) -name "*.c")
SOURCES_CPP	:= $(shell find -L $(SOURCEDIRS) -name "*.cpp")

# Compiler and linker flags
# -------------------------

WARNFLAGS_C	:= -Wall -Wextra -Wpedantic -Wstrict-prototypes

WARNFLAGS_CXX	:= -Wall -Wextra

ifeq ($(SOURCES_CPP),)
	LIBS	+= -lc
else
	LIBS	+= -lstdc++ -lc
endif

INCLUDEFLAGS	:= $(foreach path,$(INCLUDEDIRS),-I$(path)) \
		   $(foreach path,$(LIBDIRS),-I$(path)/include)

LIBDIRSFLAGS	:= $(foreach path,$(LIBDIRS),-L$(path)/lib)

CFLAGS		+= -g -std=gnu11 $(WARNFLAGS_C) $(DEFINES) $(INCLUDEFLAGS) -O0

CXXFLAGS	+= -g -std=gnu++14 $(WARNFLAGS_CXX) $(DEFINES) $(INCLUDEFLAGS) -O0

LDFLAGS		+= $(LIBDIRSFLAGS) $(LIBS)

# Intermediate build files
# ------------------------

OBJS		:= $(addsuffix .o,$(addprefix $(BUILDDIR)/,$(SOURCES_C))) \
		   $(addsuffix .o,$(addprefix $(BUILDDIR)/,$(SOURCES_CPP)))

DEPS		:= $(OBJS:.o=.d)

# Targets
# -------

.PHONY: all concord clean install

all: $(ELF)

$(LIBDIRS):
	@$(MKDIR) -p $@

concord: $(LIBDIRS)
	@$(MKDIR) -p libs
	$(V)$(MAKE) -C $@ debug
	PREFIX=$(CURDIR)/libs $(MAKE) -C $@ install

$(ELF): concord $(OBJS)
	@echo "  LD  $@"
	$(V)$(HOSTLD) -o $@ $(OBJS) $(LDFLAGS)

clean:
	@echo "  CLEAN  "
	$(V)$(MAKE) -C concord clean
	$(V)$(RM) $(ELF) $(BUILDDIR) $(LIBDIRS)

# Rules
# -----

$(BUILDDIR)/%.c.o : %.c
	@echo "  CC  $<"
	@$(MKDIR) -p $(@D)
	$(V)$(HOSTCC) $(CFLAGS) -MMD -MP -c -o $@ $<

$(BUILDDIR)/%.cpp.o : %.cpp
	@echo "  CXX $<"
	@$(MKDIR) -p $(@D)
	$(V)$(HOSTCXX) $(CXXFLAGS) -MMD -MP -c -o $@ $<

# Include dependency files if they exist
# --------------------------------------

-include $(DEPS)
