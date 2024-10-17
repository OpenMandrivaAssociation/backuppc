%define Name    BackupPC
%define debug_package %{nil}

%define __noautoreq 'perl\\(BackupPC::.*\\)'
%define __noautoprov 'perl\\(BackupPC::.*\\)'

Name:               backuppc
Version:            3.2.1
Release:            13
Summary:            High-performance, enterprise-grade backup system

Group:              Archiving/Backup
License:            GPLv2
Url:                https://backuppc.sourceforge.net
Source0:            http://sourceforge.net/projects/backuppc/files/backuppc/%{version}/%{Name}-%{version}.tar.gz
Source3:	    BackupPC_Admin.c
Source4:	    backuppc.service
Source5:	    backuppc.tmpfiles
Patch0:             %{name}-3.1.0-fhs.patch
Patch1:		    BackupPC-3.1.0-CVE-2009-3369.diff
# Correct upstream perl syntax (get rid of error messages at service start)
Patch2:		    BackupPC-3.2.1-CVE-2011-170886.diff
# CVE-2011-5081 will be obsoleted by next upstream version (> 3.2.1)
Patch3:		    BackupPC-3.2.1-CVE-2011-5081.diff
Patch4:		    BackupPC-3.2.1-CVE-2011-4923.diff
Requires:           sendmail-command
Requires:           apache
Requires(post):     rpm-helper
Requires(preun):    rpm-helper
Suggests:           openssh-clients
Suggests:           samba-client
Suggests:           perl(File::RsyncP)

%description
BackupPC is a high-performance, enterprise-grade system
for backing up Linux, Win32, and laptops to a server's disk.
Features include clever pooling of identical files, no client-side 
software, and a powerful Apache/CGI user interface. 

%prep
%setup -q -n %{Name}-%{version}
%patch0 -p1
%patch1 -p0
%patch2 -p0
%patch3 -p0
%patch4 -p0

rm -rf images/CVS
# fix file perms
find lib -type f -exec chmod 644 {} \;
find bin -type f -exec chmod 755 {} \;
find doc -type f -exec chmod 644 {} \;
find . -maxdepth 1 -type f -exec chmod 644 {} \;
# fix perl shellbang
find . -type f -exec perl -pi -e 's|^#!/bin/perl|#!/usr/bin/perl|' {} \;

%build
gcc %SOURCE3 -o BackupPC_Admin
# set installation directory
find . -type f -exec perl -pi -e 's|__INSTALLDIR__|%{_datadir}/%{name}|' {} \;
find . -type f -exec perl -pi -e 's|__TOPDIR__|%{_localstatedir}/lib/%{name}|' {} \;
# set configuration
# the binaries path are disabled to avoid service failure at start
perl -pi \
    -e 's|^\$Conf{BackupPCUser}.*|\$Conf{BackupPCUser} = "%{name}";|;' \
    -e 's|^\$Conf{CgiDir}.*|\$Conf{CgiDir} = "%{_var}/www/%{name}";|;' \
    -e 's|^\$Conf{InstallDir}.*|\$Conf{InstallDir} = "%{_datadir}/%{name}";|;' \
    -e 's|^\$Conf{CgiImageDirURL}.*|\$Conf{CgiImageDirURL} = "/%{name}";|;' \
    -e 's|^\$Conf{SshPath}.*|\$Conf{SshPath} = "/usr/bin/ssh";|;' \
    -e 's|^\$Conf{SmbClientPath}.*|\$Conf{SmbClientPath} = "/usr/bin/smbclient";|;' \
    -e 's|^\$Conf{NmbLookupPath}.*|\$Conf{NmbLookupPath} = "/usr/bin/nmblookup";|;' \
    -e 's|^\$Conf{PingPath}.*|\$Conf{PingPath} = "/bin/ping";|;' \
    -e 's|^\$Conf{DfPath}.*|\$Conf{DfPath} = "/bin/df";|;' \
    -e 's|^\$Conf{SplitPath}.*|\$Conf{SplitPath} = "/usr/bin/split";|;' \
    -e 's|^\$Conf{CatPath}.*|\$Conf{CatPath} = "/bin/cat";|;' \
    -e 's|^\$Conf{GzipPath}.*|\$Conf{GzipPath} = "/bin/gzip";|;' \
    -e 's|^\$Conf{Bzip2Path}.*|\$Conf{Bzip2Path} = "/usr/bin/bzip2";|;' \
    -e 's|^\$Conf{SendmailPath}.*|\$Conf{SendmailPath} = "/usr/sbin/sendmail";|;' \
    -e 's|^\$Conf{ServerInitdPath}.*|\$Conf{ServerInitdPath} = "%{_initrddir}/%{name}";|;' \
    -e 's|^\$Conf{BackupPCdPath}.*|\$Conf{BackupPCdPath} = "%{_datadir}/%{name}/bin/BackupPC";|;' \
    -e 's|^\$Conf{TarClientPath}.*|\$Conf{TarClientPath} = "/bin/tar";|;' \
    -e 's|^\$Conf{RsyncClientPath}.*|\$Conf{RsyncClientPath} = "/usr/bin/rsync";|;' \
    -e 's|^\$Conf{TopDir}.*|\$Conf{TopDir} = "/var/lib/backuppc";|;' \
    conf/config.pl

%install
# constant files
install -d -m 755 %{buildroot}%{_datadir}/%{name}
cp -pr lib %{buildroot}%{_datadir}/%{name}
cp -pr bin %{buildroot}%{_datadir}/%{name}
cp -pr doc %{buildroot}%{_datadir}/%{name}

# web files
install -d -m 755 %{buildroot}%{_var}/www/%{name}
install -m 644 images/* %{buildroot}%{_var}/www/%{name}
install -m 644 conf/*.css %{buildroot}%{_var}/www/%{name}
install -m 644 conf/*.js %{buildroot}%{_var}/www/%{name}
install -m 755 cgi-bin/BackupPC_Admin %{buildroot}%{_var}/www/%{name}/BackupPC_Admin.cgi

# variable files
install -d -m 755 %{buildroot}%{_localstatedir}/lib/%{name}
install -d -m 755 %{buildroot}%{_localstatedir}/lib/%{name}/{cpool,log,pc,pool,trash}

# perl-suidperl is no longer avaialable, use a C wrapper
install -m 4755 BackupPC_Admin %{buildroot}%{_var}/www/%{name}

# configuration
install -d -m 755 %{buildroot}%{_sysconfdir}/%{name}
install -m 644 conf/{hosts,config.pl} %{buildroot}%{_sysconfdir}/%{name}

# systemd
install -m 644 -D %{SOURCE4} %{buildroot}%{_unitdir}/%{name}.service
install -m 644 -D %{SOURCE5} %{buildroot}%{_tmpfilesdir}/%{name}.conf

# logs
install -d -m 755 %{buildroot}%{_var}/log/%{name}

# strip binary
%{__strip} %{buildroot}/var/www/%{name}/BackupPC_Admin

# apache configuration
install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf <<EOF
# BackupPC Apache configuration
Alias /%{name} %{_var}/www/%{name}

<Directory %{_var}/www/%{name}>
    Require all granted
    Options ExecCGI
    <Files BackupPC_Admin>
        SetHandler cgi-script
    </Files>
    DirectoryIndex BackupPC_Admin
</Directory>
EOF

cat > README.omv <<EOF
%{_distribution} RPM specific notes

Setup
-----
The %{_distribution} setup improves the FHS compliance wrt. that used upstream:
- /var/www/backuppc    ... files accessible from the web
- /usr/share/backuppc  ... files non-accessible from the web
- /var/lib/backuppc    ... files with varibales
- /etc/backuppc        ... both global and per-host configuration files

Backuppc user; backup-data
--------------------------
Backup-data stored in another file-system can be made accessible to backuppc
by creating a soft link from /var/www/lib to the root of the backup-data
hierarchy. If backuppc is uninstalled (urpme backuppc), this data will not
be deleted - with the exception of a cpool directory that is empty; when,
subsequently, backuppc is newly installed, cpool must be manually created
(with uid:gid = backuppc:backkuppc).

To make backuppc access backup-data that exist prior to installing backkuppc,
make sure that the user "backuppc" exists BEFORE the package is installed, and
that its uid and gid matches the ownership of that data (otherwise the
package would automatically create the user with random uid and gid values).

Lighttpd server definition
--------------------------
When using lighttpd, the following definition in /etc/lighttpd/lighttpd.conf
should work:
    $HTTP["url"] =~ "^/backuppc" {
	server.document-root = "/var/www/backuppc"
	cgi.assign = ( "BackupPC_Admin" => "" )
	index-file.names = ( "BackupPC_Admin" )
	alias.url = ( "/backuppc" => "/var/www/backuppc" )
	dir-listing.activate = "disable"
	$HTTP["remoteip"] != "127.0.0.1" { 
	    auth.backend = "htpasswd"
	    auth.backend.htpasswd.userfile = "<password-dir>/passwd/backuppc"
	    auth.require += ( "" => (	"method" => "basic",
					"realm" => "BackupPC",
					"require" => "valid-user" ) )
	}
    }
<password-dir> is the directory where you keep the passwords for your server;
the suggested definition does not require authentication if the backuppc gui
is invoked from the machine that hosts the lighttpd server
EOF


%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /bin/sh

%post
%tmpfiles_create %{name}
%_post_service %{name}

%preun
%_preun_service %{name}
if [ $1 -ne 0 ] ; then
# previous releases of backuppc had root as the owner - undo this fault
  chown backuppc:backuppc %{_sysconfdir}/%{name}
fi

%postun
%_postun_userdel %{name}

%files
%doc ChangeLog README LICENSE doc/* README.omv
# backuppc must be able to edit the config file and create backup files
%config(noreplace) %attr(0755,backuppc,backuppc) %{_sysconfdir}/%{name}
#% config(noreplace) %attr(0640,backuppc,backuppc) %{_sysconfdir}/%{name}/*
%config(noreplace) %{_webappconfdir}/%{name}.conf
%{_unitdir}/%{name}.service
%{_tmpfilesdir}/%{name}.conf
%{_datadir}/%{name}
#note: globbings like [^B]* or !(BackupPC*) don't work
%{_var}/www/%{name}/*.gif
%{_var}/www/%{name}/*.png
%{_var}/www/%{name}/*.css
%{_var}/www/%{name}/*.js
%{_var}/www/%{name}/*.ico
%attr(-,backuppc,backuppc) %{_var}/www/%{name}/BackupPC_Admin.cgi
%attr(-,backuppc,backuppc) %{_var}/www/%{name}/BackupPC_Admin
%attr(-,backuppc,backuppc) %{_var}/log/%{name}
%attr(-,backuppc,backuppc) %{_localstatedir}/lib/%{name}
