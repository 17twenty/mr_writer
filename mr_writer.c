/*
 * MrWriter - Trivial image writer tool
 *
 * Copyright (C) 2013 Nick Glynn <Nick.Glynn@feabhas.com>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation, version 2.
 */

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <libgen.h>

int main(int argc, char **argv)
{
    char link_path[1024];
    char *full_path = NULL;
    ssize_t len;

    len = readlink("/proc/self/exe", link_path, sizeof(link_path) - 1);
    if (len != -1)
        link_path[len] = '\0';
    else {
        perror("Readlink failed - ");
        exit(1);
    }

    setuid(0);
    seteuid(0);
    asprintf(&full_path, "%s/mr_writer.py", dirname(link_path));
    /* Use execv as we want the environment so no execve */
    char *args[10] = { "/usr/bin/env", "python", full_path, NULL };
    int returnValue = execv(args[0], args);
    
    /* Shouldn't get here */
    printf("Failed to exec Python script: %s\n", args[2]);
    free(full_path);
    return returnValue;
}
