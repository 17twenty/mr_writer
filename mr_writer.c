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
    asprintf(&full_path, "%s/mr_writer.py", dirname(link_path));
    system(full_path);
    free(full_path);
    return 0;
}
