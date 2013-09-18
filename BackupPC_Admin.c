#include <unistd.h>
#ifndef REAL_PATH
#define REAL_PATH "/var/www/backuppc/BackupPC_Admin.cgi"
#endif
int main(ac, av)
	char **av;
{
	    execv(REAL_PATH, av);
	        return 0;
}
