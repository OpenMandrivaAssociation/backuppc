%define Name    BackupPC

%if %{_use_internal_dependency_generator}
%define __noautoreq 'perl\\(BackupPC::.*\\)'
%define __noautoprov 'perl\\(BackupPC::.*\\)'
%else
%define _provides_exceptions perl(BackupPC::.*)
%define _requires_exceptions perl(BackupPC::.*)
%endif

Name:               backuppc
Version:            3.2.0
Release:            3
Summary:            High-performance, enterprise-grade backup system
Group:              Archiving/Backup
License:            GPL
url:                http://backuppc.sourceforge.net
Source:             http://sourceforge.net/projects/backuppc/%{Name}-%{version}.tar.gz
Source2:            %{name}.init
Patch0:             %{name}-3.1.0-fhs.patch
Patch1: BackupPC-3.1.0-CVE-2009-3369.diff
Requires:           sendmail-command
Requires:           apache
Requires(pre):      rpm-helper
Requires(preun):    rpm-helper
Requires(post):   rpm-helper
Requires(postun):   rpm-helper
Suggests:           openssh-clients
Suggests:           samba-client
Suggests:           perl(File::RsyncP)
Buildarch:          noarch

%description
BackupPC is a high-performance, enterprise-grade system
for backing up Linux, Win32, and laptops to a server's disk.
Features include clever pooling of identical files, no client-side 
software, and a powerful Apache/CGI user interface. 

%prep
%setup -q -n %{Name}-%{version}
%patch0 -p1
%patch1 -p0

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
	Require all granted
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

%preun
%_preun_service %{name}

%postun
%_postun_userdel %{name}

%files
%defattr(-,root,root)
%doc ChangeLog README LICENSE doc/* README.mdv
%config(noreplace) %{_sysconfdir}/%{name}
%config(noreplace) %{_webappconfdir}/%{name}.conf
%{_initrddir}/%{name}
%{_datadir}/%{name}
%{_var}/www/%{name}/*gif
%{_var}/www/%{name}/*png
%{_var}/www/%{name}/*js
%{_var}/www/%{name}/*css
%{_var}/www/%{name}/*ico
%attr(-,backuppc,backuppc) %{_localstatedir}/lib/%{name}
%attr(-,backuppc,backuppc) %{_var}/log/%{name}
%attr(-,backuppc,backuppc) %{_var}/www/%{name}/BackupPC_Admin.cgi




%changelog
* Sat Aug 07 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.2.0-1mdv2011.0
+ Revision: 567315
- new version

* Mon Mar 01 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.0-10mdv2010.1
+ Revision: 513151
- rely on filetrigger for reloading apache configuration begining with 2010.1, rpm-helper macros otherwise

* Thu Oct 01 2009 Oden Eriksson <oeriksson@mandriva.com> 3.1.0-9mdv2010.0
+ Revision: 452219
- P1: security fix for CVE-2009-3369 (debian)

* Thu Sep 10 2009 Thierry Vignaud <tv@mandriva.org> 3.1.0-8mdv2010.0
+ Revision: 436764
- rebuild

* Thu Jan 29 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.0-7mdv2009.1
+ Revision: 335370
- ship missing javascript file (close #47365)

* Mon Jan 19 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.0-6mdv2009.1
+ Revision: 331458
- add a few soft dependencies, as nobody want to read documentation (fix #47045)

* Wed Jul 23 2008 Thierry Vignaud <tv@mandriva.org> 3.1.0-5mdv2009.0
+ Revision: 243159
- rebuild

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Sun Feb 17 2008 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.0-3mdv2008.1
+ Revision: 170040
- fix FHS patch (fix #37746)

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu Nov 29 2007 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.0-2mdv2008.1
+ Revision: 113947
- don't provide or require private libfs

* Thu Nov 29 2007 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.0-1mdv2008.1
+ Revision: 113946
- new version

* Sun Aug 19 2007 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.0-2mdv2008.0
+ Revision: 66810
- set path for as much command as possible in default configuration (fix #32036)


* Wed Feb 28 2007 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.0-1mdv2007.0
+ Revision: 130153
- sync sources
- new version
  rediff FHS patch
  unify service script

* Wed Feb 14 2007 Guillaume Rousse <guillomovitch@mandriva.org> 2.1.2.2-3mdv2007.1
+ Revision: 120838
- LSB-compatible init script

* Fri Dec 15 2006 Guillaume Rousse <guillomovitch@mandriva.org> 2.1.2.2-2mdv2007.1
+ Revision: 97306
- move documentation under %%datadir/backuppc, as it is accessed at runtime (fix #27594)
  no need to modify main cgi file name
- Import backuppc

* Wed Aug 02 2006 Guillaume Rousse <guillomovitch@mandriva.org> 2.1.2.2-1mdv2007.0
- new version
- new webapps macros
- use herein document for README.mdv

* Wed Dec 21 2005 Guillaume Rousse <guillomovitch@zarb.org> 2.1.2-1mdk
- initial mdk package

