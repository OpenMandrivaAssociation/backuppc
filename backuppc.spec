%define name    backuppc
%define Name    BackupPC
%define version 3.1.0
%define release %mkrel 7

%define _provides_exceptions perl(BackupPC::.*)
%define _requires_exceptions perl(BackupPC::.*)

Name:               %{name}
Version:            %{version}
Release:            %{release}
Summary:            High-performance, enterprise-grade backup system
Group:              Archiving/Backup
License:            GPL
url:                http://backuppc.sourceforge.net
Source:             http://sourceforge.net/projects/backuppc/%{Name}-%{version}.tar.gz
Source2:            %{name}.init
Patch0:             %{name}-3.1.0-fhs.patch
Requires:           sendmail-command
Requires:           apache
Requires(pre):      rpm-helper
Requires(preun):    rpm-helper
# webapp macros and scriptlets
Requires(post):     rpm-helper >= 0.16
Requires(postun):   rpm-helper >= 0.16
Suggests:           openssh-clients
Suggests:           samba-client
Suggests:           perl(File::RsyncP)
BuildRequires:      rpm-helper >= 0.16
BuildRequires:      rpm-mandriva-setup >= 1.23
Buildarch:          noarch
BuildRoot:          %{_tmppath}/%{name}-%{version}

%description
BackupPC is a high-performance, enterprise-grade system
for backing up Linux, Win32, and laptops to a server's disk.
Features include clever pooling of identical files, no client-side 
software, and a powerful Apache/CGI user interface. 

%prep
%setup -q -n %{Name}-%{version}
%patch0 -p1
rm -rf images/CVS
# fix file perms
find lib -type f -exec chmod 644 {} \;
find bin -type f -exec chmod 755 {} \;
# fix perl shellbang
find . -type f -exec perl -pi -e 's|^#!/bin/perl|#!/usr/bin/perl|' {} \;

%build
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
    -e 's|^\$Conf{SshPath}.*|\$Conf{SshPath} = "";|;' \
    -e 's|^\$Conf{SmbClientPath}.*|\$Conf{SmbClientPath} = "";|;' \
    -e 's|^\$Conf{NmbLookupPath}.*|\$Conf{NmbLookupPath} = "";|;' \
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
    -e 's|^\$Conf{SmbClientPath}.*|\$Conf{TarClientPath} = "/usr/bin/smbclient";|;' \
    conf/config.pl

%install
rm -rf %{buildroot}

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
install -m 4755 cgi-bin/BackupPC_Admin %{buildroot}%{_var}/www/%{name}/BackupPC_Admin.cgi

# variable files
install -d -m 755 %{buildroot}%{_localstatedir}/lib/%{name}
install -d -m 755 %{buildroot}%{_localstatedir}/lib/%{name}/{cpool,log,pc,pool,trash}

# configuration
install -d -m 755 %{buildroot}%{_sysconfdir}/%{name}
install -m 644 conf/{hosts,config.pl} %{buildroot}%{_sysconfdir}/%{name}

# init script
install -d -m 755 %{buildroot}%{_initrddir}
install -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/%{name}

# logs
install -d -m 755 %{buildroot}%{_var}/log/%{name}

# apache configuration
install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf <<EOF
# BackupPC Apache configuration
Alias /%{name} %{_var}/www/%{name}

<Directory %{_var}/www/%{name}>
    Options ExecCGI
    DirectoryIndex BackupPC_Admin.cgi
    Allow from all
</Directory>
EOF

cat > README.mdv <<EOF
Mandriva RPM specific notes

setup
-----
The setup used here differs from default one, to achieve better FHS compliance.
- the files accessibles from the web are in /var/www/backuppc
- the files non accessibles from the web are in /usr/share/backuppc
- the variables files in /var/lib/backuppc
- both global and per-host configuration file are in /etc/backuppc
EOF

%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /bin/sh

%post
%_post_service %{name}
%_post_webapp

%preun
%_preun_service %{name}

%postun
%_postun_userdel %{name}
%_postun_webapp

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc ChangeLog README LICENSE doc/* README.mdv
%config(noreplace) %{_sysconfdir}/%{name}
%config(noreplace) %{_webappconfdir}/%{name}.conf
%{_initrddir}/%{name}
%{_datadir}/%{name}
%{_var}/www/%{name}
%attr(-,backuppc,backuppc) %{_localstatedir}/lib/%{name}
%attr(-,backuppc,backuppc) %{_var}/log/%{name}
%attr(-,backuppc,backuppc) %{_var}/www/%{name}/BackupPC_Admin.cgi


